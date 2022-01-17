# Universal Extractor

A Linux, Python attempt at a universal extractor similar to the Windows
[UniExtract2](https://github.com/Bioruebe/UniExtract2). 

The idea is to support the compressed archives that UniExtract2 supports but in
a Linux environment with a Python API.

### Configuration Format

```json
{
    "name": "ACB",
    "comment": "A DOS compression utility by George Buyanovsky - http://fileformats.archiveteam.org/wiki/ACB_(compressed_archive)",
    "extensions": ["acb"],
    "install": {
        "method": "apt",
        "packages": ["dosbox"],
        "tool": "ACB.EXE",
        "container": "dos/acb/acb_200c.zip"
    },
    "pack": {
        "exe": "dosbox",
        "cmdline": "$tool -noconsole -c \"mount d $tools\" -c \"mount e $(pwd)\" -c \"e:\" -c \"d:acb b $file.acb $file\" -c \"exit\"",
        "type": "dosbox"
    },
    "unpack": {
        "exe": "dosbox",
        "cmdline": "$tool -noconsole -c \"mount d $tools\" -c \"mount e $destdir\" -c \"mount f $arcloc\" -c \"d:acb r f:$shortname e:\" -c \"exit\"",
        "extension": "acb",
        "force_extension": true
    },
    "test": {
        "blob": "H4sIAACF0WEAA+Nq4GDosSx+OvP57Ps8j/mCX3MBABFWmRcSAAAA",
        "file": "0",
        "content": "ACB",
        "padbyte": "0x41",
        "padlen": 260,
        "delete": true
    },
    "identification": {
        "file": "None",
        "trid": "None",
        "idarc": "ACB"
    }
}
```

- Install methods supported:
    - `apt` (`sudo apt install <packages[0]> <packages[1]> ...`)
    - `pip` (`sudo pip install <packages[0]> <packages[1]> ...`)
    - `source` (`git clone <repo>`)
        - Adds more fields:
            - `repo` - the git repo - (currently only git is supported)
            - `build` - build script
            - `exist_check` - allows you to bypass cloning and installing if the tool is already on your system
            - Example:
                ```json
                    "install": {
                    "method": "source",
                    "repo": "https://github.com/kubo/snzip",
                    "build": "apt install libsnappy-dev && ./autogen.sh && ./configure --with-static-snappy && make && cp snzip $tools",
                    "exist_check": ["snzip -h", "Usage: snzip"]
                },
                ```
- Pack field types:
    - `archiver` - a packer we can run natively exists to generate a testable archive file
    - `dosbox` - a packer we can run via DOSbox exists to generate a testable archive file
    - `wine` - a packer we can run via Wine exists to generate a testable archive file
    - `blob` - no archiver we can run exists but we have an extractor we can test with a base64 blob of data 
    - Adds another field:
        - `blob` - the base64 encoded archive
        - Example:
            ```json
            "pack":{
                "type":"blob",
                "blob":"RUdHQQABpuPSNQAAAAAiguII45CFCgAAAAADAA=="
            },
            ```
- Representative Samples:
    - `archiver` type:
        - [zip](defs/zip.json)
            - Pretty standard Linux CLI tool that keeps a record of the original filename 
              and can archive many files in one archive.
        - [gzip](defs/gzip.json)
            - Pretty standard Linux CLI tool that has no notion of the pre-compression file metadata.
        - [dar](defs/dar.json)
            - An awful tool to use and requires backflips to extract from but shows how we can do it still.
        - [cru](defs/cru.json)
            - A CP/M archiver that is supported using [deark](https://github.com/jsummers/deark). Deark is
            an amazing extractor but its default output filename support is weird so even if the archive stores 
            the filename `0` the output is like `0.000.0` or some incremental number up from there. There
            is a flag (`-nonames`) to support not doing this but I haven't experimented yet.
    - `dosbox` type:
        - [gca](defs/gca.json)
            - Standard DOS archiver, the config was autogenerated using [dosarc.py](dosarc.py).
    - `wine` type:
        - [777](defs/777.json)
            - Standard Win32 CLI driven archiver, configuration was autogenerated using [winearc.py](winearc.py)
            and tweaked slightly to use the `-o.` flag.
    - `blob` type:
        - [egg](defs/egg.json)
            - Windows 32/64bit archiver exists but nothing we can drive from the command line so a blob of an archive 
            was created in windows. Linux extractors exist.
        - [squeeze2](defs/squeeze2.json)
            - CP/M era archiver. CP/M binary executors exist on Linux like [tnylpo](https://gitlab.com/gbrein/tnylpo)
            but they weren't working for this use case somehow. So blobs it is.

### How To Use

```
./extract.py -e <archive> -d <destination_folder>
```


### Supported Formats

| Archive type   | Common file extension(s)                                     |
| -------------- | ------------------------------------------------------------ |
| 7-zip          | .7z, .exe, .001                                              |
| ACE            | .ace, .exe                                                   |
| ALZip          | .alz                                                         |
| ARC            | .arc                                                         |
| ARJ            | .arj, .exe                                                   |
| BCM            | .bcm                                                         |
| BGA            | .bza, .gza                                                   |
| bzip2          | .bz2, .tbz2, .tar.bz2                                        |
| CPIO           | .cpio                                                        |
| DGCA           | .dgc                                                         |
| FreeArc¹       | .arc                                                         |
| gzip archive   | .gz, .tgz, .tar.gz, .ipk                                     |
| KGB            | .kgb, kge, .exe                                              |
| Linux packages | .deb, .rpm                                                   |
| LBR            | .lbr, .lzr, .lqr                                             |
| LZIP           | .lz                                                          |
| LZH            | .lzh, .lha                                                   |
| LZMA           | .lzma                                                        |
| LZO            | .lzo                                                         |
| LZW            | .Z, .tz, .tar.Z                                              |
| LZX            | .lzx                                                         |
| RAR            | .rar, .exe, .001, .r00, .part1.rar                           |
| StuffIt        | .sit, sitx                                                   |
| TAR            | .tar, ctar                                                   |
| UHARC          | .uha                                                         |
| UPX            | .exe, .dll                                                   |
| XZ             | .xz, .txz, .tar.xz                                           |
| ZIP            | .zip, .jar, .xpi, .wz, .exe, .imz                            |
| Zoo            | .zoo                                                         |
| ZPAQ           | .zpaq                                                        |

### Author

- Kris Hunt (@CTFKris)