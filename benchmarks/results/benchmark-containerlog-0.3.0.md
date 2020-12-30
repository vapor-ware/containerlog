| Benchmark | std logger (ns) | std proxy (ns) | containerlog (ns) |
| --------- | --------------- | -------------- | ----------------- |
| baseline | 0.68 +/- 0.02 | 0.69 +/- 0.01 | 0.7 +/- 0.02 |
| silent | 108.0 +/- 6.0 | 1140.0 +/- 50.0 | 51.7 +/- 1.7 |
| basic | 4750.0 +/- 160.0 | 1140.0 +/- 60.0 | 1070.0 +/- 50.0 |
| short-simple | 5370.0 +/- 160.0 | 1280.0 +/- 60.0 | 1330.0 +/- 60.0 |
| long-simple | 5280.0 +/- 180.0 | 1480.0 +/- 70.0 | 2120.0 +/- 60.0 |
| short-complex | 5630.0 +/- 170.0 | 1500.0 +/- 150.0 | 1480.0 +/- 80.0 |
| long-complex | 6900.0 +/- 190.0 | 2870.0 +/- 80.0 | 3260.0 +/- 80.0 |
| exception | 10400.0 +/- 300.0 | 4440.0 +/- 150.0 | 4370.0 +/- 500.0 |