import sys

def readArgs(args, params):
    """
    Function which translates command line arguments and acts on them.
    :param args: List of arguments to the command line.
    """
    i=0
    updates = {}
    while i < len(args):
        if args[i] in ["help", "Help", "-h", "H", "h", "?", "??"]:
            with open("README.md", "r") as readme:
                print(readme.read())
                exit()
        elif args[i] == "-T": 
            try:
                updates["T"] = float(args[i+1])
                i += 2
            except:
                print("Unrecognised temperature.")
                exit()
        elif args[i] in ["-RS", "-rs"]: 
            try:
                updates["Seed"] = float(args[i+1])
                i += 2
            except:
                print("Unrecognised seed.")
                exit()
        elif args[i] in ["-k", "-K"]:
            try:
                updates["k"] = float(args[i+1])
                i += 2
            except:
                print("Unrecognised value for -k.")
                exit()
        elif args[i] in ["-j", "-J"]:
            try:
                updates["J"] = float(args[i+1])
                i += 2
            except:
                print("Unrecognised value for J.")
                exit()
        elif args[i] in ["-x", "-X"]:
            try:
                updates["X Dimension"] = int(float(args[i+1]))
                i += 2
            except:
                print("Unrecognised value for -x.")
                exit()
        elif args[i] in ["-N", "-n"]:
            try:
                updates["tMax"] = int(float(args[i+1]))
                i += 2
            except:
                print("Unrecognised value for -N.")
                exit()
        elif args[i] in ["-e", "-E"]:
            try:
                updates["Equilibration Time"] = int(float(args[i+1]))
                i += 2
            except:
                print("Unrecognised value for -E.")
                exit()
        elif args[i] in ["-C", "-c"]:
            try:
                updates["Autocorrelation"] = int(float(args[i+1]))
                i += 2
            except:
                print("Unrecognised value for -C.")
                exit()
        elif args[i] in ["-y", "-Y"]:
            try:
                updates["Y Dimension"] = int(float(args[i+1]))
                i += 2
            except:
                print("Unrecognised value for -y.")
                exit()
        elif args[i] in ["-D", "-d"]:
            try:
                updates["Dynamics"] = args[i+1]
                i += 2
            except:
                print("Error with -d tag.")
        elif args[i] in ["-A", "-a"]:
            try:
                if args[i+1] in ["Y", "y"]:
                    updates["Animate"] = True
                    i += 2
                elif args[i+1] in ["N", "n"]:
                    updates["Animate"] = False
                    i += 2
                else:
                    print("-A should be followed by 'Y' or 'N'.")
                    exit()
            except:
                print("Error with -A tag.")
                exit()
        elif args[i] in ["-M", "-m"]:
            try:
                if args[i+1] in ["Y", "y"]:
                    updates["Measure"] = True
                    i += 2
                elif args[i+1] in ["N", "n"]:
                    updates["Measure"] = False
                    i += 2
                else:
                    print("-M should be followed by 'Y' or 'N'.")
                    exit()
            except:
                print("Error with -M tag.")
                exit()
        elif args[i] in ["-I", "-i"]:
            try:
                if args[i+1] in ["R", "r"]:
                    updates["Initial"] = "R"
                    i += 2
                elif args[i+1] in ["U", "u"]:
                    updates["Initial"] = "U"
                    i += 2
                elif args[i+1] in ["S", "s"]:
                    updates["Initial"] = "S"
                    i += 2
                else:
                    print("-I should be followed by 'U', 'R', or 'S'.")
                    exit()
            except:
                print("Error with -M tag.")
                exit()
        elif args[i] in ["-r", "-R"]:
            try:
                updates["Output"] = args[i+1]
                i += 2
            except:
                print("Unrecognised value for -o.")
                exit()
        elif args[i] in ["-o", "-O"]:
            try:
                updates["outDir"] = args[i+1]
                i += 2
            except:
                print("Unrecognised value for -o.")
                exit()
        else:
            print("Key {} not recognised. Ignoring.".format(args[i]))
    params.update(updates)
        
        
                
            
            
