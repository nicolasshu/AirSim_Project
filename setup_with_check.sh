# This must be from the .../research/ folder

# PROTOBUF COMPILATION
#     The Tensorflow Object Detection API uses Protobufs to configure model and
#     training parameters. Before the framework can be used, the Protobuf
#     libraries must be compiled. This should be done by running the following
#     command from the tensorflow/models/research/ directory:
protoc object_detection/protos/*.proto --python_out=.

# Add Libraries to PYTHONPATH
#     When running locally, the tensorflow/models/research/ and slim directories
#     should be appended to PYTHONPATH. This can be done by running the
#     following from tensorflow/models/research/:
export PYTHONPATH=$PYTHONPATH:`pwd`:`pwd`/slim

# Test installation
python object_detection/builders/model_builder_test.py
