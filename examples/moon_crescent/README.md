# How to draw a Moon crescent

## Problem

Suppose we want to draw a Moon crescent by carving it out from a Moon using a shadow overlay.

We know how big we want the Moon to be and how thick the crescent should be.

How do we draw the shadow circle?

## Formalisation

We need to know how far the center of this circle should be from the center of the Moon and how big should it be.

So we need an expression of:
- the distance $d$ of the center of the shadow circle from the center of the Moon
- the radius of the shadow circle $r_s$

... in terms of:
- the radius of the Moon $r$
- the width of the crescent $c$

## Solution

The main equation focuses on the line going through the two centers.
The distance between the center of the shadow circle and the outer bound of the Moon circle can be expressed in two different ways:
the radius of the shadow circle added to the width of the crescent,
or the radius of the moon added to the distance between the two centers.

$$c + r_s = r + d$$

The second equation describes how the two tips of the crescent must always be diametrically opposed on the Moon circle,
and the diameter going between them is perpendicular to the line connecting the two centers previously discussed.
Thus, each point where the shadow circle intersects with the Moon circle form a right triangle with the two circle centers.
So the radius of the shadow circle is also the length of this triangle's hypotenuse,
with the distance between the centers and the radius of the Moon being the lengths of the other sides.

$$r_s = \sqrt{d² + r²}$$

Injecting that into the first equation:

$$c + \sqrt{d² + r²} = r + d$$

Isolating the square root:

$$r + d - c = \sqrt{d² + r²}$$

Elevating to square to get rid of square root and simplifying:

$$(r + d - c)² = d² + r²$$
$$r² + d² + c² + 2(r d - r c - d c) = d² + r²$$
$$c² + 2(r d - r c - d c) = 0$$

Isolating $d$:

$$c² + 2 r d - 2 r c - 2 d c = 0$$
$$c² + 2 d (r - c) - 2 r c = 0$$
$$2 d(r - c) = 2 r c - c²$$
$$d = \frac{2 r c - c²}{2(r - c)}$$

Simplifying and minimizing the number of operations for faster computability:

$$d = \frac{c (2r - c)}{2(r - c)}$$
$$d = \frac{c}{2}*\frac{2r - c}{r - c}$$
$$d = \frac{c}{2}*\frac{r - c + r}{r - c}$$
$$d = \frac{c}{2}*(1 + \frac{r}{r - c})$$
