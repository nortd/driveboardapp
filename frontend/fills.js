


function fills_add_by_color(color) {
  pathidx = jobhandler.vector.colors.indexOf(color)
  path = jobhandler.vector.paths[pathidx]
  // bounds =
  // fillcolor =
  console.log(color)
  console.log(path)

  // algo
  //intersect horizontal lines with path
  // sort intersections by x
  // keep segments even to odd: 0st-1nd, 2rd-3th, ... (0 indexed)

  // // update pass widgets
  // passes_clear()
  // passes_set_assignments(jobhandler.vector.passes, jobhandler.vector.colors)
  // jobhandler.render()
  // jobhandler.draw()
}


function fills_intersect(Ax, Ay, Bx, By, Dx, Dy, Ex, Ey) {
    // intersect two line segments: A-B and D-E.
    // If the lines intersect, the result contains the x and y of the
    // intersection (treating the lines as infinite) and booleans for
    // whether line segment 1 or line segment 2 contain the point
    var denominator, a, b, numerator1, numerator2, result = {
        x: null,
        y: null,
        onLine1: false,
        onLine2: false
    }
    denominator = ((Ey - Dy) * (Bx - Ax)) - ((Ex - Dx) * (By - Ay))
    if (denominator == 0) { return result }
    a = Ay - Dy
    b = Ax - Dx
    numerator1 = ((Ex - Dx) * a) - ((Ey - Dy) * b)
    numerator2 = ((Bx - Ax) * a) - ((By - Ay) * b)
    a = numerator1 / denominator
    b = numerator2 / denominator
    // ray intersection
    result.x = Ax + (a * (Bx - Ax))
    result.y = Ay + (a * (By - Ay))
    // if A-B is a segment and D-E is a ray, they intersect if:
    if (a > 0 && a < 1) {
        result.onLine1 = true
    }
    // if D-E is a segment and A-B is a ray, they intersect if:
    if (b > 0 && b < 1) {
        result.onLine2 = true
    }
    // if A-B and D-E are segments, they intersect if both are true
    return result
}
