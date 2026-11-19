"""Run once in TouchDesigner Textport with exec(open(...).read()).

Builds two MAM presets from the pre-resize source of res1. Preview geometry is
derived from the annotated map; confirm its seams against the venue's slices.
The existing level3 -> ndiout1 route and the previous layout remain available.
"""

WIDTH, HEIGHT = 8038, 5798

# Pixel coordinates, top left origin. Each surface has its own crop and orientation.
# Wall Nord is 2490 x 1200 in wall coordinates and 1200 x 2490 in the atlas.
SURFACES = (
    ("Floor", [(1100, 1200), (4326, 1200), (5960, 2108), (6838, 2108),
               (6838, 4598), (1100, 4598)], 1),
    ("Nord", [(6838, 2108), (8038, 2108), (8038, 4598), (6838, 4598)], 1),
    ("Sud", [(0, 1200), (1100, 1200), (1100, 4598), (0, 4598)], 3),
    ("West 1", [(1100, 100), (4326, 0), (4326, 1200), (1100, 1200)], 0),
    ("West 2", [(4326, 0), (6192, 0), (6192, 1200), (4326, 1200)], 0),
    ("West 3", [(6192, 0), (7072, 0), (7072, 1200), (6192, 1200)], 0),
    ("Est 2", [(1100, 4598), (4326, 4598), (4326, 5798), (1100, 5698)], 2),
    ("Est 1", [(4326, 4598), (6838, 4598), (6838, 5798), (4326, 5798)], 2),
)

SHADER = """
out vec4 fragColor;

float edge(vec2 p, vec2 a, vec2 b) {
    vec2 ab = b - a;
    vec2 ap = p - a;
    return ab.x * ap.y - ab.y * ap.x;
}

vec4 video(vec2 p, vec2 size, int turn) {
    vec2 uv = p / size;
    if (turn == 1) uv = vec2(uv.y, 1.0 - uv.x);
    if (turn == 2) uv = 1.0 - uv;
    if (turn == 3) uv = vec2(1.0 - uv.y, uv.x);
    if (turn == 1 || turn == 3) size = size.yx;
    vec2 source = uTD2DInfos[0].res.zw;
    float targetAspect = size.x / size.y;
    float sourceAspect = source.x / source.y;
    vec2 crop = vec2(min(1.0, targetAspect / sourceAspect),
                     min(1.0, sourceAspect / targetAspect));
    uv = (uv - 0.5) * crop + 0.5;
    return vec4(texture(sTD2DInputs[0], vec2(uv.x, 1.0 - uv.y)).rgb, 1.0);
}
"""

def vec(point):
    return "vec2(%.1f, %.1f)" % point


def fragment(split):
    canvas = vec((WIDTH, HEIGHT))
    lines = [SHADER, "void main() {",
             f"    vec2 p = vec2(vUV.x, 1.0 - vUV.y) * {canvas};",
             "    vec4 color = vec4(0.0, 0.0, 0.0, 1.0);"]
    for name, points, turn in SURFACES:
        edges = zip(points, points[1:] + points[:1])
        mask = " && ".join(f"edge(p, {vec(a)}, {vec(b)}) >= 0.0" for a, b in edges)
        if name == "Floor":
            mask = ("p.x >= 1100.0 && p.x < 6838.0 && p.y < 4598.0 && "
                    "p.y >= 1200.0 + 908.0 * clamp((p.x - 4326.0) / 1634.0, 0.0, 1.0)")
        xs, ys = zip(*points)
        origin = vec((min(xs), min(ys)))
        size = vec((max(xs) - min(xs), max(ys) - min(ys)))
        sample = f"video(p - {origin}, {size}, {turn})" if split else f"video(p, {canvas}, 1)"
        lines.append(f"    if ({mask}) color = {sample};")
    lines.extend(("    fragColor = TDOutputSwizzle(color);", "}"))
    return "\n".join(lines)


def connect_layout_osc(project, selector):
    receiver = project.op("oscin1")
    if receiver is None:
        print("MAM OSC: /project1/oscin1 not found. Index remains manual.")
        return
    index = selector.par.index
    fallback = int(index.eval()) if index.mode == ParMode.CONSTANT else 0
    if index.mode != ParMode.CONSTANT:
        if "elisa/fx/mam_layout" in index.expr:
            print("MAM OSC already connected.")
        else:
            print("MAM OSC: Index already has a driver. Existing driver kept.")
        return
    index.expr = (
        "next((int(chan.eval() >= 0.5) for chan in op('/project1/oscin1').chans() "
        "if chan.name.lstrip('/') == 'elisa/fx/mam_layout'), "
        f"{fallback})"
    )
    index.mode = ParMode.EXPRESSION
    print("MAM OSC ready: /elisa/fx/mam_layout (0 = Full Room, 1 = Superfici).")


def build():
    project = op("/project1")
    existing = project.op("mam_layout")
    if existing is not None:
        connect_layout_osc(project, existing)
        return
    res = project.op("res1")
    level = project.op("level3")
    ndi = project.op("ndiout1")
    if not res or not level or not ndi or not res.inputs or not level.inputs:
        raise RuntimeError("Expected /project1/res1, level3 and ndiout1.")
    previous = level.inputs[0]
    if previous != res and (not previous.inputs or previous.inputs[0] != res):
        raise RuntimeError("Expected res1 directly or as input 0 of the switch before level3.")
    if not ndi.inputs or ndi.inputs[0] != level:
        raise RuntimeError("Expected level3 to feed ndiout1.")

    created = []

    def make(kind, name):
        if project.op(name) is not None:
            raise RuntimeError(f"Node already exists: {name}")
        node = project.create(kind, name)
        created.append(node)
        return node

    try:
        selector = make(switchTOP, "mam_layout")
        selector.nodeX, selector.nodeY = level.nodeX - 160, level.nodeY - 250
        for index, name in enumerate(("mam_full_room", "mam_surfaces")):
            shader = make(textDAT, name + "_shader")
            shader.text = fragment(split=index == 1)
            top = make(glslTOP, name)
            top.nodeX, top.nodeY = selector.nodeX - 180, selector.nodeY - index * 130
            shader.nodeX, shader.nodeY = top.nodeX - 145, top.nodeY
            top.par.pixeldat = shader.path
            top.par.outputresolution = "custom"
            top.par.resolutionw = WIDTH
            top.par.resolutionh = HEIGHT
            top.par.resmult = False
            top.inputConnectors[0].connect(res.inputs[0])
            top.cook(force=True)
            if top.errors() or (top.width, top.height) != (WIDTH, HEIGHT):
                raise RuntimeError(f"{top.path}: {top.errors()} ({top.width} x {top.height})")
            top.outputConnectors[0].connect(selector)

        selector.par.index = 0
        level.inputConnectors[0].connect(selector)
    except Exception:
        if not level.inputs or level.inputs[0] != previous:
            level.inputConnectors[0].connect(previous)
        for node in reversed(created):
            node.destroy()
        raise
    connect_layout_osc(project, selector)
    print(f"MAM ready: mam_layout Index 0 = Full Room, 1 = Surfaces. Previous feed: {previous.path}")


if __name__ == "__main__":
    build()
