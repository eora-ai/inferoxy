# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: protos/inferrequest.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from protos import inputinferrequest_pb2 as protos_dot_inputinferrequest__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='protos/inferrequest.proto',
  package='',
  syntax='proto3',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\x19protos/inferrequest.proto\x1a\x1eprotos/inputinferrequest.proto\"T\n\x0cInferRequest\x12\x11\n\tsource_id\x18\x01 \x01(\t\x12\r\n\x05model\x18\x02 \x01(\t\x12\"\n\x06inputs\x18\x03 \x03(\x0b\x32\x12.InputInferRequestb\x06proto3'
  ,
  dependencies=[protos_dot_inputinferrequest__pb2.DESCRIPTOR,])




_INFERREQUEST = _descriptor.Descriptor(
  name='InferRequest',
  full_name='InferRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='source_id', full_name='InferRequest.source_id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='model', full_name='InferRequest.model', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='inputs', full_name='InferRequest.inputs', index=2,
      number=3, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=61,
  serialized_end=145,
)

_INFERREQUEST.fields_by_name['inputs'].message_type = protos_dot_inputinferrequest__pb2._INPUTINFERREQUEST
DESCRIPTOR.message_types_by_name['InferRequest'] = _INFERREQUEST
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

InferRequest = _reflection.GeneratedProtocolMessageType('InferRequest', (_message.Message,), {
  'DESCRIPTOR' : _INFERREQUEST,
  '__module__' : 'protos.inferrequest_pb2'
  # @@protoc_insertion_point(class_scope:InferRequest)
  })
_sym_db.RegisterMessage(InferRequest)


# @@protoc_insertion_point(module_scope)
