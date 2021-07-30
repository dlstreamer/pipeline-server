# Model Downloader
| [Specifying Models](#specifying-models) | [Downloading Models](#downloading-models) | [Reference](#command-line-reference) |

The model downloader downloads and prepares models from the
OpenVINO<sup>&#8482;</sup> Toolkit [Open Model
Zoo](https://github.com/openvinotoolkit/open_model_zoo) for use with
Video Analytics Serving. It can be run as a standalone tool or as
part of the Video Analytics Serving build process. For more
information on model file formats and the directory structure used by
Video Analytics Serving see [defining_pipelines](/docs/defining_pipelines.md#deep-learning-models).

# Specifying Models

Models are specified using a yaml file containing a list of model
entries. Model entries can either be strings (model names) or objects
(model names plus additional properties) and a single yaml file can
contain both forms of entries. An [example file](/models_list/models.list.yml) is used as part of the
default build process.

## String Entries
String entries specify the model to download from the [Open Model
Zoo](https://github.com/openvinotoolkit/open_model_zoo). The model and
model-proc files will be downloaded and stored locally using [default
values](#default-values).

Example:

```yaml
- mobilenet-ssd
- emotions-recognition-retail-0003
```

## Object Entries
Object entries specfiy the model to download from the [Open Model
Zoo](https://github.com/openvinotoolkit/open_model_zoo) and one or
more optional properties (alias, version, precision, local
model-proc). If an optional property is not specified the downloader
will use [default values](#default-values).

Example:

```yaml
- model: yolo-v3-tf
  alias: object_detection
  version: 2
  precision: [FP32,INT8]
  model-proc: object_detection.json
```

## Default Values

* alias = model_name
* version = 1
* precision = all available precisions
* model-proc = model_name.json

If a local model-proc is not specified, the tool will download the
corresponding model-proc file from the DL streamer repository (if one
exists).


# Downloading Models

The model downloader can be run either as a standalone tool or as part
of the Video Analytics Serving build process.

## Downloading Models as part of Video Analytics Serving Build

The Video Analytics Serving build script downloads models listed in a
yaml file that can be specified via the `--models` argument.

Example:
```bash
./docker/build.sh --models models_list/models.list.yml
```

## Downloading Models with the standalone tool

When run as a standalone tool, the model downloader will run within an
`openvino/ubuntu20_data_dev:2021.4` docker image and download models listed in
a yaml file that can be specified via the  `--model-list` argument.

Example:
```bash
mkdir standalone_models
./tools/model_downloader/model_downloader.sh --model-list models_list/models.list.yml --output ${PWD}/standalone_models
```

### Command Line Reference

```bash
usage: model_downloader.sh
  [--output absolute path where to save models]
  [--model-list input file with model names and properties]
  [--force force download and conversion of existing models]
  [--open-model-zoo-version specify the version of openvino image to be used for downloading models from Open Model Zoo]
  [--dry-run print commands without executing]
```
