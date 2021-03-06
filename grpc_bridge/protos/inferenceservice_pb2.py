# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: protos/inferenceservice.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from protos import inferrequest_pb2 as protos_dot_inferrequest__pb2
from protos import inferresult_pb2 as protos_dot_inferresult__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='protos/inferenceservice.proto',
  package='',
  syntax='proto3',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\x1dprotos/inferenceservice.proto\x1a\x19protos/inferrequest.proto\x1a\x18protos/inferresult.proto2:\n\x10InferenceService\x12&\n\x05Infer\x12\r.InferRequest\x1a\x0c.InferResult\"\x00\x62\x06proto3'
  ,
  dependencies=[protos_dot_inferrequest__pb2.DESCRIPTOR,protos_dot_inferresult__pb2.DESCRIPTOR,])



_sym_db.RegisterFileDescriptor(DESCRIPTOR)



_INFERENCESERVICE = _descriptor.ServiceDescriptor(
  name='InferenceService',
  full_name='InferenceService',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_start=86,
  serialized_end=144,
  methods=[
  _descriptor.MethodDescriptor(
    name='Infer',
    full_name='InferenceService.Infer',
    index=0,
    containing_service=None,
    input_type=protos_dot_inferrequest__pb2._INFERREQUEST,
    output_type=protos_dot_inferresult__pb2._INFERRESULT,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
])
_sym_db.RegisterServiceDescriptor(_INFERENCESERVICE)

DESCRIPTOR.services_by_name['InferenceService'] = _INFERENCESERVICE

# @@protoc_insertion_point(module_scope)
