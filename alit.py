#!/usr/bin/env python3
from os import system as sys
from sys import exit
from subprocess import run, PIPE, Popen
from time import sleep


class alit:
    version = "0.6"
    logo = """
   ##    #      ###  #####
  #  #   #       #     #
 ######  #       #     #
#      # #####  ###    #
Arch Linux Installation Tool Version {}""".format(version)
    cpright = "Licensed Under GNU GPLv2\nCoding By M.J. Bagheri Nejad"
    def chpath(self):
        chp = int(input(
            "\n\t1 - CMD Installtion\n\t2 - GUI Installtion\n\t3 - Exit\n\t=> "
        ))
        if chp == 1:
            self.cmdi()
        elif chp == 2:
            self.guii()
        elif chp == 3:
            self.ex()
        else:
            self.chpath()

    def __init__(self):
        print("{}\n{}".format(self.logo, self.cpright))
        self.chpath()

    @property
    def cmdi(self):
        # Geting The Hostname
        hn = str(input("Please Enter Your Hostname: "))

        # Geting The Username
        self.usrn = str(input(
            "(if you dont want a seprate user leave empty)\nPlease Enter Your Username: "))

        # Geting The Root Password
        rootpass = str(input("Please Enter Your Root Password: "))

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

        # Change root into the new system, Set the time zone, Localization, Create the hostname file
        chro = Popen(["arch-chroot", "/mnt"],
            stdin=PIPE,stderr=PIPE,stdout=PIPE)
        cmd = "ln -sf /usr/share/zoneinfo/Europe/ /etc/localtime && hwclock --systohc && echo 'en_US.UTF-8 UTF-8' >> /etc/locale.gen && locale-gen && touch /etc/locale.conf && echo 'LANG=en_US.UTF-8' > /etc/locale.conf && echo '{}' > /etc/hostname && echo '127.0.0.1\\tlocalhost\\n::1\\tlocalhost\\n127.0.1.1\\t{}' > /etc/hosts && pacman -S networkmanager && mkinitcpio -P && passwd".format(
            hn,
            hn,
        )
        chro.communicate(input=bytes(cmd, "utf-8"))
        sleep(15)
        chro.communicate(input=b"\n")

        # Creating a new initramfs, Set the root password
        sleep(40)
        chro.communicate(input=bytes(rootpass))

        # Boot loader
        bl = "pacman -S grub && grub-install {} && exit".format(iDevice)
        chro.communicate(input=bytes(bl, "utf-8"))
        sleep(15)
        chro.communicate(input=b"\n")


        self.chpath()


    @property
    def guii(self):
        self.cmdi()
        gpu = run(["lspci","-v","|","grep","-A1","-e","VGA","-e","3D"],
        stdout=PIPE).stdout.decode("UTF-8")
        if gpu.find("intel") == -1 | gpu.find("Intel") == -1:
            gpud = "xf86-video-intel"
        elif gpu.find("nvidia") == -1 | gpu.find("Nvidia") == -1:
            gpud = "nvidia"
        elif gpu.find("amd") == -1 | gpu.find("AMD") == -1:
            gpud = "xf86-video-amdgpu"
        sys("pacman -S xorg xterm lightdm lightdm-gtk-greeter pulseaudio pavucontrol {} && systemctl enable lightdm".format(gpud))
        appl = str(input("Please Enter Your App List if you have one (Default: ./qtileAL.txt): "))
        if appl == "":
            appl == "./qtileAL.txt"
        self.ins(appl)
        if self.usrn != "":
            sys("useradd -m -G wheel -s /bin/fish {}".format(self.usrn))
    
    @property
    def ins(self, s):
        s = str(s)
        f = open(s, "r")
        lins = f.readlines()
        cmd = "pacman -S"
        for lin in lins:
            cmd = "{} {}".format(cmd, lin)
        
        f.close()
        sys(cmd)
        sys("chsh -s /bin/fish")

    @property
    def ex(self):
        sys("umount -R /mnt")
        sys("reboot")


alit()
