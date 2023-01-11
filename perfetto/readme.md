# Updating Perfetto Trace

Perfetto uses protobuf to read the trace files, why not use it to generate the trace files as well?

The [aggreagated proto file](https://github.com/google/perfetto/blob/76e503101931100a2f0073bc22be4e48a6e1083e/protos/perfetto/trace/perfetto_trace.proto) is available from github, then we need to generate the protobuf python bindings with the following command:

```bash
pip install grpc_tools.protoc
python -m grpc_tools.protoc -I=./ --python_out=./ --pyi_out=./ perfetto_trace.proto
```
