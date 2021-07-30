# Object Line Crossing
The object line crossing spatial analytics extension is used in tandem with gvatrack to determine when tracked objects cross virtually defined lines supplied to the extension.

## Parameters
The extension takes the following parameters. The `lines` parameter is required, all others are optional.

### lines
A list of line definitions, which are objects containing the following fields:
* `name` the name of the line for use in event reporting.
* `line` a tuple of (x,y) coordinates defining the start and end of the directional line segment.

```json
"lines": [
    {
        "name": "hallway_right",
        "line": [[0.9,0.8],[0.8,0.45]]
    },
    {
        "name": "hallway_left",
        "line": [[0.15,0.45],[0.05,0.75]]
    },
    {
        "name": "hallway_bottom",
        "line": [[0.1,0.9],[0.8,0.9]]
    }
]
```
### enable_watermark
A `boolean` flag that defaults to `false`. If set to `true` annotations are added, with `n_start`, `n_end` to mark the start and end of line `n` from lines (list is 0 based) will be added to rendered watermark images. Another annotation `n_count` midway along the line indicates the total number of crossing events for that line.

### log_level
The [logging level](https://docs.python.org/3.8/library/logging.html#logging-levels) defined as a `string`. Defaults to "INFO".

## Event Output
If a tracked object crosses any of the lines, an event of type `object-line-crossing` will be created with the following fields.
* `line-name`: name of the associated line
* `related-detections`: array containing indexes of the detected objects that crossed the line
* `directions` : array containing directions which can be `clockwise`, `counterclockwise`, or `parallel`. The orientation is determined from from line-start to line-end.
* `clockwise-total` : total number of clockwise crossings
* `counterclockwise-total` : total number of counter clockwise crossings
* `total` : total number of crossings

JSON example is shown below

```json
{
   "event-type":"object-line-crossing",
   "line-name":"hallway_bottom",
   "related-objects": [
      0
   ],
   "directions":[
      "counterclockwise"
   ],
   "clockwise-total":"0",
   "counterclockwise-total":"1",
   "total":"1"
}
```

## Line Crossing Algorithm
The algorithm to calculate line crossing is based on the following article:
https://www.geeksforgeeks.org/check-if-two-given-line-segments-intersect/
