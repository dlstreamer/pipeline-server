# Zone Event Detection
The Zone Event Detection AI Skill is used to determine if detected objects reside in polygons that this Skill takes as inputs.

## Parameters
The extension takes the following parameters. All parameters are optional for the pipeline to run.

### zones
A list of zone definitions which are objects containing the following fields.
* `name` : the name of the zone for use in event reporting.
* `polygon` : A list of four vertices (a tuple of x,y coordinates) which make up the bounds of the polygon.

**If this parameter is not set, the extension defaults to an empty list and will not check for zone detections.**

```json
"zones": [
    {
        "name": "Zone1",
        "polygon": [[0.01,0.10],[0.005,0.53],[0.11,0.53],[0.095,0.10]]
    },
    {
        "name": "Zone2",
        "polygon": [[0.14,0.20],[0.18,0.67],[0.35,0.67],[0.26,0.20]]
    },
    {
        "name": "Zone3",
        "polygon": [[0.40,0.30],[0.50,0.83],[0.85,0.83],[0.57,0.30]]
    }
]
```
### enable_watermark
A `boolean` flag that defaults to `false`. If set to `true` marks the vertices of all zones and annotates the first vertex with the zone name.

### log_level
The [logging level](https://docs.python.org/3.8/library/logging.html#logging-levels) defined as a `string`. Defaults to "INFO".

## Event Output
If a tracked object crosses any of the lines, an event of type `object-zone-count` will be created with the following fields.
* `zone-name`: name of the associated line
* `related-detections`: array containing the array indices of the detected objects in the zone
* `status` : array containing the status of the detected objects in the zone. Values can be `"within"` to indicate that the object is fully within the zone or `"intersects"` if it touches any of the vertices.
* `zone-count` : total number of objects in the zone

```json
{
   "event-type":"zoneCrossing",
   "zone-name":"Zone1",
   "related-objects":[
      0, 1, 4
   ],
   "status":[
      "within",
      "within",
      "intersects"
   ],
   "zone-count" : 3
}
```
