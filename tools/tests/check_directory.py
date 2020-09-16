import os
import sys

def check_directory(path, name, alias=None, version=1, precision="FP32"):
    # If alias not provided, set alias to model name
    if alias == None:
        alias = name

    # Check to see if folder was created in alias/version path
    model_path = os.path.join(os.path.abspath(path), 'models', alias, str(version))
    assert os.path.isdir(model_path)

    # Check to see if model proc exists
    model_proc_name = name + '.json'
    model_proc_file = os.path.join(model_path, model_proc_name)
    assert os.path.isfile(model_proc_file)

    # Check to see if precision folder exists
    model_precision_path = os.path.join(model_path, precision)
    assert os.path.isdir(model_precision_path)

    # Check to see if xml exists
    model_xml_name = name + '.xml'
    model_xml_file = os.path.join(model_precision_path, model_xml_name)
    assert os.path.isfile(model_xml_file)

    # Check to see if bin exists
    model_bin_name = name + '.bin'
    model_bin_file = os.path.join(model_precision_path, model_bin_name)
    assert os.path.isfile(model_bin_file)

def check_directory_yml(path, name, version=1, precision="FP32"):

    # Check to see if folder was created in modelname/version path
    model_path = os.path.join(os.path.abspath(path), 'models', name, str(version))
    assert os.path.isdir(model_path)

    # Check to see if model proc exists
    model_proc_name = name + '.json'
    model_proc_file = os.path.join(model_path, model_proc_name)
    assert os.path.isfile(model_proc_file)

    # Check to see if precision folder exists
    model_precision_path = os.path.join(model_path, precision)
    assert os.path.isdir(model_precision_path)

    # Check to see if xml exists
    model_xml_name = name + '.xml'
    model_xml_file = os.path.join(model_precision_path, model_xml_name)
    assert os.path.isfile(model_xml_file)

    # Check to see if bin exists
    model_bin_name = name + '.bin'
    model_bin_file = os.path.join(model_precision_path, model_bin_name)
    assert os.path.isfile(model_bin_file)