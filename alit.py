#!/usr/bin/env python3
from os import system as sys
from sys import exit
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
    il = ""
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
        hn = str(input("Please Enter Your Hostname: "))

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
        sys("mount {} /mnt".format(rootdev))
        if homedev != "":
            sys("mount {} /mnt/home".format(homedev))

        # Install essential packages
        sys("pacstrap /mnt base linux linux-firmware")

        # Generate an fstab file
        sys("genfstab -L /mnt >> /mnt/etc/fstab")

        # Change root into the new system, Set the time zone, Localization, Create the hostname file, Creating a new initramfs, Set the root password
        cmd = "ln -sf /usr/share/zoneinfo/Europe/ /etc/localtime && hwclock --systohc && echo 'en_US.UTF-8 UTF-8' >> /etc/locale.gen && locale-gen && touch /etc/locale.conf && echo 'LANG=en_US.UTF-8' > /etc/locale.conf && echo '{}' > /etc/hostname && echo '127.0.0.1\\tlocalhost\\n::1\\tlocalhost\\n127.0.1.1\\t{}' > /etc/hosts && mkinitcpio -P && passwd".format(
            hn,
            hn,
        )
        run(["arch-chroot", "/mnt", cmd]) 
        
        # Boot loader
        bl = "pacman -S networkmanager grub && grub-install {}".format(
            iDevice)
        run(["arch-chroot", "/mnt", bl])

        #IL
        self.il = "./cmdIL"
        self.ins()

        #Adding User
        if self.usrn != "":
            cmd = "useradd -m -G wheel -s /bin/fish {}".format(self.usrn)
            run(["arch-chroot", "/mnt", cmd])

        # Exiting
        if self.chp == 1:
            self.ex()

    def guii(self):
        self.cmdi()
        gpu = run(["lspci -v | grep -A1 -e VGA -e 3D"],
        stdout=PIPE).stdout.decode("UTF-8")
        if gpu.find("intel") == -1 | gpu.find("Intel") == -1:
            gpud = "xf86-video-intel"
        elif gpu.find("nvidia") == -1 | gpu.find("Nvidia") == -1:
            gpud = "nvidia"
        elif gpu.find("amd") == -1 | gpu.find("AMD") == -1:
            gpud = "xf86-video-amdgpu"
        cmd = "pacman -S xorg xterm lightdm lightdm-gtk-greeter pulseaudio pavucontrol {} && systemctl enable lightdm".format(
            gpud)
        run(["arch-chroot", "/mnt", cmd])
        il = str(input("Please Enter Your App List if you have one (Default: ./qtileAL.txt): "))
        if il == "":
            self.il = "./qtileAL.txt"
        else:
            self.il = il
        self.ins()
        self.ex()
    
    def ins(self):
        f = open(self.il, "r")
        lins = f.readlines()
        cmd = "pacman -S"
        for lin in lins:
            cmd = "{} {}".format(cmd, lin)
        f.close()
        cmd = "{} {}".format(cmd, "&& chsh -s /bin/fish")
        run(["arch-chroot", "/mnt", cmd])

    def ex(self):
        sys("umount -R /mnt")
        sys("reboot")

if __name__ == "__main__":
    alit()
