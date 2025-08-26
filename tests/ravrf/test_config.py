from pathlib import Path
import struct
import sys

srcPath = f"{Path.cwd()}/../../src/ravrf"
sys.path.append(srcPath)
import config

def test_getStorageSize():
    assert config.RavrfConfig.getStorageSize() == 22

def test_config_create():
    cfg = config.RavrfConfig()
    assert cfg is not None
    assert cfg.meta_address == 0
    assert cfg.first_available_address == 0    

def test_config_encode_new():
    cfg = config.RavrfConfig()
    data = cfg.encode()
    assert isinstance(data, bytearray)
    assert len(data) == 22
    assert data[0:11] == b"/~ ravrf ~/"
    assert data[11] == 1
    assert struct.unpack(">I", data[12:16])[0] == 0
    assert struct.unpack(">I", data[16:20])[0] == 0

def test_config_encode_custom():
    cfg = config.RavrfConfig(version=1, meta_address=123456, first_available_address=654321, checksum=793)
    data = cfg.encode()
    print(f'encoded data: {data}')
    assert isinstance(data, bytearray)
    assert len(data) == 22
    assert data[0:11] == b"/~ ravrf ~/"
    assert data[11] == 1
    assert struct.unpack(">I", data[12:16])[0] == 123456
    assert struct.unpack(">I", data[16:20])[0] == 654321    