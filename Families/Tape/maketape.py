import math, random
import ynlib.beziers
reload(ynlib.beziers)
from ynlib.beziers import *

size(500, 500)

points = (Point(100, 100), Point(400, 100))
points = (Point(100, random.randint(100, 400)), Point(400, random.randint(100, 400)))

strokeWidth(1)
#stroke(0, 0, 0)
fill(0, 0, 0)

tapeWidth = 100
glitchHeight = 2

newPath()
moveTo((points[0].x, points[0].y))
lineTo((points[1].x, points[1].y))
closePath()
drawPath()


 


def glitch(p1, p2, w):
    

    probabilityOfGlitches = random.random() < .95
    
    if probabilityOfGlitches:
        points = [p1]
        currentPoint = p1
        numberOfGlitches = random.randint(1, 2)
        
        glitchPositions = []
        if numberOfGlitches == 1:
            glitchPositions.append(random.randint(30, 70)/100)
        elif numberOfGlitches == 2:
            glitchPositions.append(random.randint(20, 40)/100)
            glitchPositions.append(random.randint(60, 80)/100)
        

        tapeWidthLeft = w
        glitchLengths = []
        glitchWidthSum = 0
        print 'glitchPositions', glitchPositions
        for glitchPosition in glitchPositions:
            glitchLength = w * glitchPosition - glitchWidthSum
            glitchWidthSum += glitchLength
            glitchLengths.append(glitchLength)
            tapeWidthLeft -= glitchLength
        glitchLengths.append(tapeWidthLeft)

        print 'glitchLengths', glitchLengths, 'sum', sum(glitchLengths)
        
        glitchWidthSum = 0

        for glitchLength in glitchLengths:
            
            delta = p2 - p1 
            if delta.x != 0:
                slope = delta.y/delta.x
            else:
                slope = -1
            distance = p1.distance(p2)
            
            tapeWidthLeft = tapeWidthLeft - glitchLength
            
            glitchWidthSum += glitchLength

            if (p2.x-p1.x) != 0:
                m = (p2.y-p1.y)/(p2.x-p1.x)
            else:
                m = 0
    
            if m != 0:
                im = -1/m
            else:
                im = -1
            

            g1 = currentPoint + (p2 - p1) * (1/distance) * glitchLength
            direction = random.choice([-1, 1])

            
            if delta.x != 0:
                g2 = Point(g1.x + 1 * glitchHeight * direction, g1.y - 1/slope * glitchHeight * direction)
            else:
                g2 = Point(g1.x + 1 * glitchHeight * direction, g1.y - 0 * glitchHeight * direction)

#            g2 = Point(p1.x + glitchHeight * 1 / distance * m, p1.y + glitchHeight * im / distance * m)
            
            currentPoint = g2
            
            points.append(g1)
            points.append(g2)

        points = points[:-1]
#        g1 = currentPoint + (p2 - p1) * (1/distance) * (w-glitchWidthSum)
#        points.append(g1)
        
        # Add glitches
        # for glitchPosition in glitchPositions:
            

        #     delta = p2 - p1 
        #     if delta.x != 0:
        #         slope = delta.y/delta.x
        #     else:
        #         slope = 0
        #     distance = p1.distance(p2)
            
        #     glitchLength = tapeWidthLeft * glitchPosition
        #     tapeWidthLeft = tapeWidthLeft - glitchLength
            
        #     glitchWidthSum += glitchLength
            
        # #     print 'glitchPosition', glitchPosition

        #     g1 = currentPoint + (p2 - p1) * (1/distance) * glitchLength
        #     direction = random.choice([-1, 1])
        #     g2 = Point(g1.x + 1 * glitchHeight * direction, g1.y - 1/slope * glitchHeight * direction)
            
        #     currentPoint = g2
            
        #     points.append(g1)
        #     points.append(g2)
            
        
        # g1 = currentPoint + (p2 - p1) * (1/distance) * tapeWidthLeft
        # points.append(g1)
        

        return points
        
        
        
        
        
        
    else:
        print 'Not glitching'
        return [p1, p2]
        
    
        




def tape(p1, p2, w):
    
    
    points = []

    
    delta = p2 - p1    
    dx = p2.x - p1.x
    dy = p2.y - p1.y
    distance = math.sqrt(dx**2 + dy**2)
    d = Point((p2.x - p1.x) / distance, (p2.y - p1.y) / distance)
    m = (p2.y-p1.y)/(p2.x-p1.x)
    
    wa = 100/66.6666666666666 * 100

    if m != 0:
        im = -1/m
        c1 = Point(p1.x + w * wa * 1 / distance * m, p1.y + w * wa * im / distance * m)

    else:
        c1 = Point(p1.x, p1.y + w/2)
    
    
    # Plain corner points
#    c1 = Point(p1.x + w * 1 / distance, p1.y + w * im / distance)
    c2 = c1 + delta
    c3 = c2 - (c1 - p1) * 2
    c4 = c1 - (c1 - p1) * 2
    
    print 'resulting width', c4.distance(c1)
    
    points.extend(reversed(glitch(c1, c4, w)))
    points.extend(glitch(c2, c3, w))


#    points.extend([c1, c2, c3, c4])

    
    return points
    



newPath()

miny=500
maxy=0

for i, point in enumerate(tape(points[0], points[1], tapeWidth)):

    #print point
    miny = min(miny, point.y)
    maxy = min(maxy, point.y)

    if i == 0:
        newPath()
        moveTo((point.x, point.y))
    else:
        lineTo((point.x, point.y))

closePath()
drawPath()


print miny - maxy