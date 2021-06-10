#!/usr/bin/env python3
from os import system as sys
from sys import exit, argv
from subprocess import run, PIPE


class alit:
    version = "0.6"
    logo = """
   ##    #      ###  #####
  #  #   #       #     #
 ######  #       #     #
#      # #####  ###    #
Arch Linux Installation Tool Version {}""".format(version)
    cpright = "Licensed Under GNU GPLv2\nCoding By M.J. Bagheri Nejad"
    il = argv[1]
    tlin = ""
    def chpath(self):
        self.chp = int(input(
            "\n\t1 - CMD Installtion\n\t2 - GUI Installtion\n\t3 - Exit\n\t=> "
        ))
        if self.chp == 1:
            self.cmdi()
        elif self.chp == 2:
            self.guii()
        elif self.chp == 3:
            self.ex()
        else:
            self.chpath()

    def __init__(self):
        print("{}\n{}".format(self.logo, self.cpright))
        self.chpath()

    def cmdi(self):
        # Geting The Hostname
        self.hn = str(input("Please Enter Your Hostname: "))

        # Geting The Username
        self.usrn = str(input(
            "(if you dont want a seprate user leave empty)\nPlease Enter Your Username: "))

        # Geting The Root Password
        #rootpass = str(input("Please Enter Your Root Password: "))

        # Listing The Devices
        sys("fdisk -l")

        # Choose The Disk
        iDevice = str(
            input("Choose the disk that you want to install on it ( /dev/sda ) => "))
        if iDevice == "":
            iDevice = "/dev/sda"
        
        # Update the system clock
        sys("timedatectl set-ntp true")

        # Check if its UEFI
        chuefi = run(["ls", "/sys/firmware/efi/efivars"],
                     stdout=PIPE).stdout.decode("UTF-8")
        if chuefi.find("No such file or directory") == -1:
            print("BIOS")
            # Partition the disks
            sys("pacman -S cfdisk")
            sys("cfdisk {}".format(iDevice))
            sys("clear")
        else:
            print("UEFI: Not Supported")
            exit()

        # Mount the file systems
        sys("fdisk -l")
        rootdev = str(input("which one is the root partition? "))
        homedev = str(
            input("which one is the home partition (if you dont have one press enter)? "))
        sys("mkfs.ext4 {} && mount {} /mnt".format(rootdev, rootdev))
        if homedev != "":
            hmkfs = str(
                input("Do you want to format the home partition (y/N)? "))
            if hmkfs == "y":
                sys("mkfs.ext4 {} && mount {} /mnt/home".format(homedev, homedev))
            elif hmkfs == "" | hmkfs == "n" | hmkfs == "N":
                sys("mount {} /mnt/home".format(homedev))

        # Install essential packages
        sys("pacstrap /mnt base linux linux-firmware fish vim micro ranger sudo networkmanager grub")

        # Generate an fstab file
        sys("genfstab -L /mnt >> /mnt/etc/fstab")

        #Adding User
        if self.usrn != "":
            self.tlin = f"useradd -m -G wheel -s /bin/fish {self.usrn}"
            self.achrosh()

        # Change root into the new system, Set the time zone, Localization, Create the hostname file
        # Boot loader, Creating a new initramfs
        if self.chp == 1:
            self.rchrosh()
        
        #IL
        self.ins()

        # Set the root password
        print("----Set the root password----")
        run(["arch-chroot", "/mnt", "passwd"])
        
        # Exiting
        if self.chp == 1:
            self.ex()

    def guii(self):
        # Runing The CMD Installation
        self.cmdi()

        # Getting The Graphic Card Chipset Brand
        gpu = run(["lspci -v | grep -A1 -e VGA -e 3D"], stdout=PIPE).stdout.decode("UTF-8")
        if gpu.find("intel") == -1 | gpu.find("Intel") == -1:
            gpud = "xf86-video-intel"
        elif gpu.find("nvidia") == -1 | gpu.find("Nvidia") == -1:
            gpud = "nvidia"
        elif gpu.find("amd") == -1 | gpu.find("AMD") == -1:
            gpud = "xf86-video-amdgpu"
        
        # Installing xServer, Display Manager, Sound Driver, Graphic Driver
        sys(f"pacstrap /mnt xorg xterm lightdm lightdm-gtk-greeter pulseaudio pavucontrol {gpud}")

        # Editing chrosh and executing
        self.tlin = "systemctl enable lightdm"
        self.achrosh()
        self.rchrosh()

        # Installing pkgs from ILs
        self.ins()

        # Exiting
        self.ex()
    
    def ins(self):
        f = open(self.il, "r")
        lins = f.readlines()
        cmd = "pacstrap /mnt"
        for lin in lins:
            cmd = f"{cmd} {lin}"
        f.close()
        cmd = cmd.replace("\n", "");cmd = cmd.replace("\t", "")
        sys(cmd)
    
    def rchrosh(self):
        run(["cp", "./chrosh.bash", "/mnt/usr/bin/chrosh"])
        run(["chmod", "+x", "/mnt/usr/bin/chrosh"])
        run(["arch-chroot", "/mnt", "chrosh", self.hn])
    
    def achrosh(self):
        f = open("./chrosh.fish", "a")
        f.writelines(self.tlin)
        f.close()

    def ex(self):
        sys("umount -R /mnt")
        sys("reboot")

if __name__ == "__main__":
    alit()
