# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: protos/parametermessage.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='protos/parametermessage.proto',
  package='',
  syntax='proto3',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\x1dprotos/parametermessage.proto\"d\n\x10ParameterMessage\x12\x12\n\nbool_param\x18\x01 \x01(\x08\x12\x11\n\tint_param\x18\x02 \x01(\x05\x12\x13\n\x0b\x66loat_param\x18\x03 \x01(\x01\x12\x14\n\x0cstring_param\x18\x04 \x01(\tb\x06proto3'
)




_PARAMETERMESSAGE = _descriptor.Descriptor(
  name='ParameterMessage',
  full_name='ParameterMessage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='bool_param', full_name='ParameterMessage.bool_param', index=0,
      number=1, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='int_param', full_name='ParameterMessage.int_param', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='float_param', full_name='ParameterMessage.float_param', index=2,
      number=3, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='string_param', full_name='ParameterMessage.string_param', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
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
  serialized_start=33,
  serialized_end=133,
)

DESCRIPTOR.message_types_by_name['ParameterMessage'] = _PARAMETERMESSAGE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

ParameterMessage = _reflection.GeneratedProtocolMessageType('ParameterMessage', (_message.Message,), {
  'DESCRIPTOR' : _PARAMETERMESSAGE,
  '__module__' : 'protos.parametermessage_pb2'
  # @@protoc_insertion_point(class_scope:ParameterMessage)
  })
_sym_db.RegisterMessage(ParameterMessage)


# @@protoc_insertion_point(module_scope)
