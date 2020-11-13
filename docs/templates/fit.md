# Fit.py
This is the main function taking a transmission spectrum as input and producing a metasurface stack as output.

## Usage
Help to all scripts can be revived with the `-h` option. `fit -h`:

<pre><code>
fit.py [-h] [-m MODEL] [-db DATABASE] [-S SMATS] [-i INDEX] [-I] s

positional arguments:
  s                     path to target spectrum .npy file

optional arguments:
  -h, --help            show this help message and exit
  -m MODEL, --model MODEL
                        path to trained model model
  -db DATABASE, --database DATABASE

                        sqlite database containing the adresses
  -S SMATS, --smats SMATS
                        directory containing the smats for interpolation
  -i INDEX, --index INDEX
  -I, --interpolate
 </code></pre>

The target spectrum has to be provided as a `.npy` array of shape `L x 2` where `L` is the number of sampled wavelengths and the `2` contains X - and Y - polarization. The provided model `stacker.h5` has been trained on a dataset with `L = 160`

___

## Source Code



{{autogenerated}}