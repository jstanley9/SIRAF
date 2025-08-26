from pathlib import Path
import sys

srcPath = f"{Path.cwd()}/../../src/ravrf"
sys.path.append(srcPath)
import config

def main():
    cfg = config.RavrfConfig(version=1, meta_address=1_903_326_068, first_available_address=1_145_258_561, checksum=725)
    data = cfg.encode()
    print(f'encoded data: {data}')
    print('As hex string: ', data.hex())

    cfg2 = config.RavrfConfig.decode(data)
    assert cfg2 is not None
    assert cfg2.meta_address == 1_903_326_068
    assert cfg2.first_available_address == 1_145_258_561
    data2 = cfg2.encode()
    if data != data2:    
        print(f'encoded data2: {data2}')
        raise ValueError("Encoded data does not match after decode")

if __name__ == "__main__":
    main()    