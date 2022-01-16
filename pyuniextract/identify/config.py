import os.path

trid_defs = "/usr/share/trid/triddefs.trd"
trid_args = ['/usr/local/bin/trid', '-n:1', f'-d:{trid_defs}']
trid_env = {"LC_ALL":"C"}

idarcbin = os.path.join(os.path.dirname(os.path.realpath(__file__)),'../..','tools','idarc')

packerNames = {1:'ARC', 2:'ZIP', 3:'ZOO',  4:'LZH', 5:'DWC', 6:'MDCD', 7:'LBR', 8:'ARJ', 9:'HYP', 10:'UC2', 11:'HAP', 12:'HA',
                13:'HPack', 14:'SQZ(SqueezeIt)', 15:'RAR', 16:'PAK', 17:'ARC+', 18:'LIM', 19:'BSN(BSA/PTS-DOS)', 20:'PUT', 21:'SQWEZ', 22:'Crush/ZIP',
                23:'Crush/ARJ', 24:'Crush/LZH', 25:'Crush/ZOO', 26:'Crush/HA', 27:'LZExe', 28:'PKLite', 29:'Diet', 30:'TinyProg', 31:'GIF', 32:'JPG(JFIF)',
                33:'JPG(HSI)', 34:'AIN', 35:'AINEXE', 36:'SAR', 37:'BS2/BSArc', 38:'GZIP/Comp4.3', 39:'ACB', 40:'MAR', 41:'CPZ(CPShrink)',
                42:'JRC', 43:'JArcs', 44:'Quantum', 45:'ReSOF', 46:'Crush/uncomp.', 47:'ARX', 48:'UCEXE', 49:'WWPack', 50:'QuArk', 51:'YAC',
                52:'X1', 53:'Codec', 54:'AMGC', 55:'NuLIB', 56:'PAKLeo(PLL)', 57:'TGZ', 58:'WWPackdatafile', 59:'ChArc', 60:'PSA', 61:'ZAR',
                62:'LHark', 63:'CrossePAC', 64:'Freeze', 65:'KBoom', 66:'NSQ', 67:'DPA', 68:'TTComp', 69:'WIC(Fake!)', 70:'RKive', 71:'JAR', 72:'ESP',
                73:'ZPack', 74:'DRY', 75:'OWS(Fake!)', 76:'SKY', 77:'ARI', 78:'UFA', 79:'MicrosoftCAB', 80:'FOXSQZ', 81:'AR7',
                82:'TSComp', 83:'PPMZ', 84:'MSCompress', 85:'MP3(MarcoCzudej)', 86:'ZET', 87:'XPackData', 88:'XPackDiskimage', 89:'ARQ', 90:'ACE',
                91:'Squash', 92:'Terse', 93:'XPacksingledata', 94:'Stuffit(Mac)', 95:'PUCrunch', 96:'BZip', 97:'UHarc', 98:'ABComp', 99:'CMP(Andre Olejko)',
                100:'BZip2', 101:'LZO', 102:'szip', 103:'Splint', 104:'TAR', 105:'InstallShield', 106:'CARComp', 107:'LZS', 108:'BOA', 109:'InstallShieldZ',
                110:'ARG', 111:'Gather', 112:'PackMagic', 113:'BTS', 114:'ELI5750', 115:'QFC', 116:'PRO-PACK', 117:'MSXiE', 118:'RAX', 119:'777',
                120:'LZS221', 121:'HPA', 122:'Arhangel', 123:'EXP1', 124:'IMP', 125:'BMF', 126:'NRV', 127:'oPAQue', 128:'Squish(MikeAlbert)', 129:'Par',
                130:'HIT(BogdanUreche)', 131:'SBX', 132:'NaShrink', 133:'Disintegrator', 134:'ASD', 135:'InstallShieldCAB', 136:'TOP4', 137:'BatComp(4DOS)',
                138:'BlakHole', 139:'BIX(IgorPavlov)', 140:'ChiefLZA', 141:'Blink(D.T.S.)', 142:'CAR(MylesHi!)', 143:'SARJ', 144:'CompackSfx',
                145:'LogitechCompress', 146:'ARS-Sfx', 147:'AKT', 148:'Flash', 149:'PC/3270', 150:'NPack', 151:'PFT', 152:'Xtreme', 153:'SemOne',
                154:'AKT32', 155:'InstallIt', 156:'PPMD', 157:'Swag', 158:'FIZ', 159:'BA(M.Lundqvist)', 160:'XPA32(J.Tseng)', 161:'RK(M.Taylor)',
                162:'RPM', 163:'DeepFreezer', 164:'ZZip(DamienDebin)', 165:'DC(EdgarBinder)', 166:'TPac(TimGordon)', 167:'Ai(E.Ilya)', 168:'Ybs(VadimYoockin)',
                169:'Ai32(E.Ilya)', 170:'SBC(SamiM�kinen)', 171:'DitPack',  172:'DMS', 173:'EPC', 174:'VSARC', 175:'PDZ', 176:'PackagefortheWeb',
                177:'NullSoftInstaller', 178:'WiseInstaller', 179:'DZip(NolanPflug)', 180:'7z', 181:'ReDuq(J.Mintjes)', 182:'aPackage', 183:'WinImage',
                184:'GCA', 185:'PPMN(MaxSmirnov)', 186:'SAPCAR', 187:'Compressia', 188:'UHBC', 189:'PKZip6/BZip2'}