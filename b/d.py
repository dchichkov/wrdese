ids = \
{'bad': [87922, 7267547, 7267809, 8062750, 10055187, 10509469, 10530468, 11750964, 11756997, 11914828, 12227040, 12523054, 13463133, 13660213,
         14272280, 14272850, 14275079, 14948164, 20525968, 20629438, 20629608, 22840818, 22844172, 23282700, 24328279, 27182665, 27640833, 27851052,
         28506867, 28506952, 28520865, 28520898, 28520985, 28977208, 29481113, 29596265, 30672651, 31214807, 31214949, 31214999, 31807153, 36271161,
         36653046, 38069689, 38069851, 38070156, 38455163, 38455235, 38455470, 38455512, 38455576, 38455600, 39061269, 39671070, 39672035, 39672352,
         39672810, 39944676, 39944791, 44076221, 44076355, 44745798, 44745879, 45718227, 46033144, 46033434, 46035098, 46035574, 47562565, 47831095,
         47831298, 47832319, 47930699, 49035656, 49035876, 49517482, 49803780, 49819228, 51053804, 51056413, 51375526, 51375756, 51375868, 52348144,
         54512902, 54512985, 54949396, 55167603, 55321837, 55338724, 55405680, 55514113, 56934860, 58150017, 59731219, 62240704, 62810078, 63364037,
         64442722, 64794424, 64794762, 65784924, 67162250, 67247217, 68383652, 68987830, 72350059, 75896729, 75897438, 76766612, 76862662, 76958471,
         77707456, 78309640, 78310050, 78918668, 79254503, 79254995, 79289996, 79832301, 79931016, 79994212, 82243683, 82538001, 82544343, 83205274,
         83205493, 83311704, 83324297, 83673966, 83831474, 83831523, 85164737, 85164824, 86089951, 86288578, 86707374, 86707827, 86842879, 86843565,
         86843885, 86946526, 87551908, 87551977, 87552036, 87552090, 87552118, 87552149, 87552207, 88086348, 89053520, 89110083, 90325273, 90690356,
         90945062, 91285305, 91384434, 91385250, 91868312, 91868465, 92567999, 92568316, 92568386, 92568564, 92568754, 92568932, 92569075, 92569113,
         92569223, 92569314, 92570772, 92587807, 92834258, 93665263, 93665931, 93669958, 93675138, 93915996, 94201176, 94347221, 94558261, 95165921,
         95210934, 95517928, 95518138, 95636064, 97131644, 97200560, 98050628, 98105980, 98646749, 98682247, 99591813, 99859627, 99970462, 100785619,
         101201526, 101321218, 101348928, 101483585, 101853266, 102243380, 102719125, 102996745, 103267404, 103282592, 103323528, 104235133],
 'bad (corrected by user)': [22844172, 27640833, 27851052, 36271161, 46035098, 47831095, 47831298, 47832319, 47930699, 49035656, 49035876, 63364037,
                             64442722, 65784924, 75896729, 76862662, 78309640, 78310050, 82243683, 82538001, 82544343, 83324297, 87551908, 87551977,
                             87552036, 87552090, 87552118, 87552149, 87552207, 89053520, 93675138, 95165921, 97131644, 98646749, 101321218,
                             101483585],
 'bad (verified by user)': [87922, 7267547, 7267809, 8062750, 10055187, 10509469, 10530468, 11750964, 11756997, 11914828, 12227040, 12523054,
                            13463133, 13660213, 14272280, 14272850, 14275079, 14948164, 20525968, 20629438, 20629608, 22840818, 23282700, 24328279,
                            27182665, 28506867, 28506952, 28520865, 28520898, 28520985, 28977208, 29481113, 29596265, 30672651, 31214807, 31214949,
                            31214999, 31807153, 36653046, 38069689, 38069851, 38070156, 38455163, 38455235, 38455470, 38455512, 38455576, 38455600,
                            39061269, 39671070, 39672035, 39672352, 39672810, 39944676, 39944791, 44076221, 44076355, 44745798, 44745879, 45718227,
                            46033144, 46033434, 46035574, 47562565, 49517482, 49803780, 49819228, 51053804, 51056413, 51375526, 51375756, 51375868,
                            52348144, 54512902, 54512985, 54949396, 55167603, 55321837, 55338724, 55405680, 55514113, 56934860, 58150017, 59731219,
                            62240704, 62810078, 64794424, 64794762, 67162250, 67247217, 68383652, 68987830, 72350059, 75897438, 76766612, 76958471,
                            77707456, 78918668, 79254503, 79254995, 79289996, 79832301, 79931016, 79994212, 83205274, 83205493, 83311704, 83673966,
                            83831474, 83831523, 85164737, 85164824, 86089951, 86288578, 86707374, 86707827, 86842879, 86843565, 86843885, 86946526,
                            88086348, 89110083, 90325273, 90690356, 90945062, 91285305, 91384434, 91385250, 91868312, 91868465, 92567999, 92568316,
                            92568386, 92568564, 92568754, 92568932, 92569075, 92569113, 92569223, 92569314, 92570772, 92587807, 92834258, 93665263,
                            93665931, 93669958, 93915996, 94201176, 94347221, 94558261, 95210934, 95517928, 95518138, 95636064, 97200560, 98050628,
                            98105980, 98682247, 99591813, 99859627, 99970462, 100785619, 101201526, 101348928, 101853266, 102243380, 102719125,
                            102996745, 103267404, 103282592, 103323528, 104235133],
 'good': [74064, 87900, 87901, 95087, 102258, 105239, 190653, 278830, 278831, 278832, 278833, 278834, 278835, 278836, 278837, 311213, 316123,
          316133, 318757, 403660, 485817, 508208, 780749, 828182, 846256, 1118969, 1180279, 1441510, 1573479, 1882827, 1957362, 1985727, 2287576,
          2287611, 2287625, 2287634, 2287665, 2287688, 2287707, 2287728, 2287778, 2287785, 2288224, 2288244, 2288368, 2288372, 2298609, 2306865,
          2651654, 2745298, 2820665, 2820677, 2900140, 3076901, 3078487, 3250607, 3250754, 3250764, 3264842, 3360307, 3419401, 3563398, 3563763,
          3567630, 3585848, 3707246, 3708476, 3783822, 3828720, 3828748, 3828978, 3832117, 3832125, 3861886, 4300215, 4577291, 4844949, 4845514,
          4854011, 4854159, 4854179, 4854263, 5041265, 5041286, 5131948, 5158376, 5181662, 5575752, 5575853, 5722079, 5863333, 6200065, 6202527,
          6282893, 6341309, 6408366, 6456716, 6456758, 6463322, 6518044, 6596041, 6596054, 6596133, 6621456, 6712504, 6724313, 6724329, 6748707,
          6802729, 7059890, 7060009, 7267463, 7267741, 7340580, 7941361, 8057609, 8099468, 8744770, 8746687, 8757370, 8758215, 9244764, 9282518,
          9294704, 9856873, 10052536, 10100894, 10106274, 10106909, 10110462, 10118102, 10486567, 10509294, 10509317, 10530384, 10554442, 10666398,
          10739734, 10841175, 10842248, 11181715, 11202759, 11290873, 11319680, 11461930, 11493447, 11493502, 11750866, 11914366, 11995257,
          12227019, 12522924, 12605137, 12772008, 12773201, 12779329, 12804140, 12804853, 12839452, 12845841, 12853640, 12853997, 13117615,
          13117678, 13117691, 13150041, 13462301, 13523289, 13656142, 13893154, 13981845, 14184686, 14272224, 14926047, 14982155, 15222917,
          15252585, 15413245, 15417777, 15421364, 15661390, 15895896, 15922890, 18055865, 18639011, 18801342, 18814048, 18814060, 18864896,
          19066365, 19444458, 19640863, 19836813, 20225370, 20225961, 20226150, 20226255, 20226811, 20542270, 20631122, 20915675, 21458354,
          22176761, 22378410, 22378499, 22561169, 22665748, 22665843, 22665955, 23013457, 23287732, 23426148, 23545372, 23545929, 23546446,
          23546544, 24329454, 24345103, 24487838, 24488002, 24488196, 24488861, 24488968, 25178051, 27182713, 27270148, 27383519, 27386474,
          27386621, 27638740, 28527237, 28527269, 28977490, 29482810, 29628497, 29700683, 29764123, 30297938, 30672686, 30894941, 30896119,
          30897421, 30900484, 30900796, 30901017, 30901369, 30901542, 31153923, 31215039, 31721836, 31748782, 31861139, 32483307, 32756122,
          32820602, 32884638, 33140431, 33166416, 33208875, 33267816, 35396071, 36271320, 36457256, 36466021, 36658004, 37068268, 37073973,
          37175157, 37243770, 37801593, 38069739, 38069872, 38070212, 38539072, 38564266, 39064824, 39390902, 39444821, 39444946, 39547898,
          39671101, 39716432, 39756905, 39944686, 39944828, 40070177, 42229928, 43738117, 44077664, 44489853, 44489944, 44702722, 44745895,
          45728184, 46052432, 46204176, 47495368, 47562662, 47760470, 47943104, 47991664, 48167172, 48265048, 48968847, 49035868, 49035913,
          49496907, 49517488, 49739075, 49819318, 51041574, 51056428, 51063159, 51091416, 51313229, 51375974, 51725256, 51884068, 52348207,
          53796471, 53990177, 53990270, 53990740, 53990876, 53990991, 53991400, 53991631, 53991845, 53991967, 53992282, 53992424, 53992466,
          53993275, 53993396, 54014759, 54180882, 54513017, 54953662, 55172390, 55321849, 55340633, 55407127, 55435820, 55514315, 55701617,
          55769737, 56950656, 57060980, 57267188, 57441468, 57967329, 58150093, 58347960, 58977033, 58977328, 59731272, 61177065, 62207331,
          62240720, 62812186, 62843253, 62843370, 62862970, 63613168, 64344753, 64685934, 64696539, 64699018, 64794856, 65377564, 65395910,
          65561381, 65561582, 65634235, 66090689, 66358032, 67162272, 67248020, 67940375, 68383671, 68990470, 69500270, 69500399, 69500537,
          69502257, 69502381, 70253765, 70271196, 70654465, 70794970, 71600146, 71965376, 72357252, 72887553, 73361141, 73501286, 73904924,
          75189599, 75189849, 75189997, 75481666, 75481872, 75897469, 75897574, 75898731, 75900582, 76667978, 76773183, 76976107, 77494373,
          77494447, 77687296, 77752519, 77818162, 77961062, 77961248, 77961435, 78036436, 78042656, 78309657, 78310340, 78939334, 79254835,
          79278988, 79291200, 79832306, 79934255, 79994785, 80033331, 80033491, 80966115, 81065636, 81712848, 81713038, 82208780, 82243859,
          82540982, 82541589, 82541832, 82543254, 82544074, 82554593, 82928309, 83008711, 83205769, 83311796, 83328056, 83674683, 83675002,
          84216004, 85019936, 85167118, 85225372, 85735258, 86052344, 86095941, 86096140, 86110137, 86288860, 86707869, 86845679, 86993024,
          87317883, 87490674, 87552213, 88114285, 89055740, 89110440, 90228563, 90294509, 90325362, 90690048, 90690452, 90945232, 91287738,
          91384445, 91390454, 91662163, 91668144, 91870638, 92568969, 92571213, 92591295, 93571790, 93666151, 93916187, 94201253, 94235281,
          94352769, 94589842, 95025347, 95166175, 95517933, 95518238, 95641432, 97200685, 97989857, 98052515, 98106094, 98206161, 98682639,
          98763420, 98891587, 99593302, 99864523, 100015544, 100065433, 100786160, 100990986, 100991332, 100991450, 101201815, 101352707, 101854575,
          101871739, 101877238, 101881437, 101990232, 102246136, 102725090, 102913097, 102996924, 103274975, 103285097, 103326174, 103415335,
          103534343, 103534636, 103799475, 104235189, 104237772, 104238074],
 'good (corrected by user)': [87901, 12522924, 13893154, 67248020, 79254835, 86288860, 90690048, 104235189],
 'good (verified by user)': [95087, 2288224, 3861886, 7267463, 7267741, 7340580, 8057609, 8099468, 9282518, 9294704, 10052536, 10100894, 10106274,
                             10106909, 10110462, 10118102, 10486567, 10509294, 10509317, 10530384, 10554442, 10841175, 11202759, 11493447, 11493502,
                             11750866, 11914366, 11995257, 12227019, 12605137, 12772008, 13462301, 13523289, 13656142, 13981845, 14184686, 14272224,
                             14926047, 14982155, 15252585, 15922890, 18639011, 18814048, 18814060, 19444458, 20226811, 20542270, 20631122, 20915675,
                             22561169, 22665955, 23013457, 23287732, 23545372, 23546544, 24329454, 24487838, 24488861, 25178051, 27182713, 27383519,
                             28527237, 28527269, 28977490, 29482810, 29628497, 29764123, 30297938, 30672686, 30896119, 30900484, 31153923, 31215039,
                             31748782, 31861139, 33140431, 33208875, 33267816, 36271320, 36466021, 36658004, 37801593, 38069739, 38069872, 38070212,
                             38539072, 38564266, 39064824, 39390902, 39547898, 39671101, 39716432, 39756905, 39944686, 39944828, 42229928, 43738117,
                             44077664, 44489853, 44702722, 44745895, 45728184, 46052432, 47495368, 47562662, 47943104, 47991664, 48968847, 49035868,
                             49035913, 49496907, 49517488, 49739075, 49819318, 51056428, 51063159, 51091416, 51313229, 51375974, 51725256, 51884068,
                             52348207, 53991967, 54180882, 54513017, 54953662, 55172390, 55321849, 55340633, 55407127, 55435820, 55514315, 55769737,
                             56950656, 57060980, 57267188, 57441468, 57967329, 58150093, 58977328, 59731272, 62207331, 62240720, 62812186, 64344753,
                             64699018, 64794856, 65561381, 66090689, 66358032, 67162272, 67940375, 68383671, 68990470, 69500270, 69500399, 69502257,
                             70253765, 70654465, 71965376, 72357252, 73904924, 75481872, 75897469, 75897574, 76667978, 76773183, 76976107, 77494373,
                             77687296, 77752519, 78036436, 78042656, 78309657, 78310340, 78939334, 79278988, 79291200, 79832306, 79934255, 79994785,
                             82208780, 82243859, 82540982, 82544074, 82554593, 83008711, 83205769, 83311796, 83328056, 83674683, 83675002, 85019936,
                             85167118, 86052344, 86095941, 86096140, 86110137, 86707869, 86845679, 86993024, 87317883, 87552213, 88114285, 89055740,
                             89110440, 90294509, 90325362, 90690452, 90945232, 91287738, 91384445, 91390454, 91662163, 91668144, 91870638, 92568969,
                             92571213, 92591295, 93571790, 93666151, 93916187, 94201253, 94235281, 94352769, 94589842, 95025347, 95166175, 95517933,
                             95518238, 95641432, 97200685, 97989857, 98052515, 98106094, 98682639, 98891587, 99593302, 99864523, 100015544,
                             100065433, 100786160, 100991450, 101201815, 101352707, 101854575, 101990232, 102246136, 102725090, 102913097, 102996924,
                             103274975, 103285097, 103326174, 103415335, 103799475]}