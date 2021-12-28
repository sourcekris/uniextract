# Universal Extractor

A Linux, Python attempt at a universal extractor similar to the Windows
[UniExtract2](https://github.com/Bioruebe/UniExtract2). 

The idea is to support the compressed archives that UniExtract2 supports but in
a Linux environment with a Python API.

### Configuration Format

```json
{
    "name":"ZIP",
    "extensions":["zip", "jar", "xpi", "wz", "exe", "imz", "apk", "docx", "docm"],
    "install": {
        "method":"apt",
        "package":"unzip"
    },
    "unpack": {
        "exe":"unzip",
        "cmdline":"$tool $archive -d $destdir",
        "extension":"zip",
        "force_extension": true
    },
    "test": {
        "blob":"H4sIAOL0ymEAAwvwZmbhYgCBhs1zgs9c33WFGcgGYUYGGQaD0BBOBuYDX04lgnBpBTcDIwtILZiI8gwI8GZkkmPGpV8CLM4IxEsaQSygaawQ09BMCvBmZYMoZWRwB9J2YI0AHG5Bv5sAAAA=",
        "file":"0",
        "content":"ZIP"
    }
}
```

### Supported Formats

TBD

### To Do Archive Formats

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
| PEA            | .pea                                                         |
| RAR            | .rar, .exe, .001, .r00, .part1.rar                           |
| StuffIt        | .sit, sitx                                                   |
| TAR            | .tar, .tbz2, .tgz, .txz, .tz, .tar.bz2, .tar.gz, .tar.xz, .tar.Z, ctar |
| UHARC          | .uha                                                         |
| UPX            | .exe, .dll                                                   |
| XZ             | .xz, .txz, .tar.xz                                           |
| ZIP            | .zip, .jar, .xpi, .wz, .exe, .imz                            |
| Zoo            | .zoo                                                         |
| ZPAQ           | .zpaq                                                        |

### Author

- Kris Hunt (@CTFKris)