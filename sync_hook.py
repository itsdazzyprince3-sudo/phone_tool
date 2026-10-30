# 🎭 VirgoYT Auto-Update Hook
# Add this function to your phone_tool.py:

import subprocess

def auto_sync_git():
    """
    Checks the GitHub remote for new commits, pulls them down,
    and automatically restarts the tool on the new version.
    """
    print()
    glitch_line()
    print(f"  {C.CYAN}⚡ CHECKING FOR UPDATES (GITHUB SYNC)...{C.RST}")
    glitch_line()

    try:
        # Fetch the latest commit info silently
        loadbar("CONNECTING TO REMOTE", 20, 0.4)
        subprocess.run(["git", "fetch", "origin"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Check if local is behind origin
        status = subprocess.check_output(["git", "status", "-uno"]).decode("utf-8")
        
        if "Your branch is behind" in status:
            print(f"\n  {C.Y}► New commits detected on GitHub remote!{C.RST}")
            loadbar("PULLING LATEST CODE", 25, 0.5)
            
            res = subprocess.run(["git", "pull", "--ff-only"], capture_output=True, text=True)
            if res.returncode == 0:
                print(f"  {C.G}✅ Successfully updated to latest version!{C.RST}")
                print(f"  {C.CYAN}⚡ Hot-restarting VirgoYT engine...{C.RST}\n")
                time.sleep(1)
                # Restart running script automatically
                os.execv(sys.executable, [sys.executable] + sys.argv)
            else:
                print(f"  {C.R}❌ Pull conflict detected: {res.stderr.strip()}{C.RST}")
        elif "Your branch is up to date" in status:
            print(f"  {C.G}✅ Toolkit is already on the latest build.{C.RST}\n")
        else:
            # Fallback direct pull
            subprocess.run(["git", "pull"], check=True)
            print(f"  {C.G}✅ Synced successfully.{C.RST}\n")
            
    except FileNotFoundError:
        print(f"  {C.R}❌ Git is not installed in this environment.{C.RST}\n")
    except subprocess.CalledProcessError as e:
        print(f"  {C.R}❌ Sync failed: Ensure remote repository is linked with 'git remote add origin ...'{C.RST}\n")
    except Exception as e:
        print(f"  {C.R}❌ Error during update: {e}{C.RST}\n")
