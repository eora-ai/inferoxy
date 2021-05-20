# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: protos/outputinfer.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from protos import inferdata_pb2 as protos_dot_inferdata__pb2
from protos import parametermessage_pb2 as protos_dot_parametermessage__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='protos/outputinfer.proto',
  package='',
  syntax='proto3',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\x18protos/outputinfer.proto\x1a\x16protos/inferdata.proto\x1a\x1dprotos/parametermessage.proto\"\xdf\x01\n\x0bOutputInfer\x12\r\n\x05shape\x18\x01 \x03(\x05\x12\x10\n\x08\x64\x61tatype\x18\x02 \x01(\t\x12\x0e\n\x06output\x18\x03 \x01(\t\x12\r\n\x05\x65rror\x18\x04 \x01(\t\x12\x18\n\x04\x64\x61ta\x18\x05 \x01(\x0b\x32\n.InferData\x12\x30\n\nparameters\x18\x06 \x03(\x0b\x32\x1c.OutputInfer.ParametersEntry\x1a\x44\n\x0fParametersEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12 \n\x05value\x18\x02 \x01(\x0b\x32\x11.ParameterMessage:\x02\x38\x01\x62\x06proto3'
  ,
  dependencies=[protos_dot_inferdata__pb2.DESCRIPTOR,protos_dot_parametermessage__pb2.DESCRIPTOR,])




_OUTPUTINFER_PARAMETERSENTRY = _descriptor.Descriptor(
  name='ParametersEntry',
  full_name='OutputInfer.ParametersEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='OutputInfer.ParametersEntry.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='value', full_name='OutputInfer.ParametersEntry.value', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=b'8\001',
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=239,
  serialized_end=307,
)

_OUTPUTINFER = _descriptor.Descriptor(
  name='OutputInfer',
  full_name='OutputInfer',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='shape', full_name='OutputInfer.shape', index=0,
      number=1, type=5, cpp_type=1, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='datatype', full_name='OutputInfer.datatype', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='output', full_name='OutputInfer.output', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='error', full_name='OutputInfer.error', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='data', full_name='OutputInfer.data', index=4,
      number=5, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='parameters', full_name='OutputInfer.parameters', index=5,
      number=6, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[_OUTPUTINFER_PARAMETERSENTRY, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=84,
  serialized_end=307,
)

_OUTPUTINFER_PARAMETERSENTRY.fields_by_name['value'].message_type = protos_dot_parametermessage__pb2._PARAMETERMESSAGE
_OUTPUTINFER_PARAMETERSENTRY.containing_type = _OUTPUTINFER
_OUTPUTINFER.fields_by_name['data'].message_type = protos_dot_inferdata__pb2._INFERDATA
_OUTPUTINFER.fields_by_name['parameters'].message_type = _OUTPUTINFER_PARAMETERSENTRY
DESCRIPTOR.message_types_by_name['OutputInfer'] = _OUTPUTINFER
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

OutputInfer = _reflection.GeneratedProtocolMessageType('OutputInfer', (_message.Message,), {

  'ParametersEntry' : _reflection.GeneratedProtocolMessageType('ParametersEntry', (_message.Message,), {
    'DESCRIPTOR' : _OUTPUTINFER_PARAMETERSENTRY,
    '__module__' : 'protos.outputinfer_pb2'
    # @@protoc_insertion_point(class_scope:OutputInfer.ParametersEntry)
    })
  ,
  'DESCRIPTOR' : _OUTPUTINFER,
  '__module__' : 'protos.outputinfer_pb2'
  # @@protoc_insertion_point(class_scope:OutputInfer)
  })
_sym_db.RegisterMessage(OutputInfer)
_sym_db.RegisterMessage(OutputInfer.ParametersEntry)


_OUTPUTINFER_PARAMETERSENTRY._options = None
# @@protoc_insertion_point(module_scope)
