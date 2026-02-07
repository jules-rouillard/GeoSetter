# GeoSetter
A small utility that sorts a folder of photos into two groups – those that already contain GPS metadata and those that don’t – and then try to add location data to those that don't.

## What It Does

1. **Categorises images**

2. **Matches by timestamp**
   - For each image missing GPS data, the tool searches for a counterpart that **has GPS metadata** and was taken at the same (or very close) date and time.
   - When a suitable match is found, the GPS coordinates from the reference image are copied into the target image.

