#!/usr/bin/env fish
ln -sf /usr/share/zoneinfo/Europe/ /etc/localtime
hwclock --systohc
echo 'en_US.UTF-8 UTF-8' >> /etc/locale.gen
locale-gen
touch /etc/locale.conf
echo 'LANG=en_US.UTF-8' > /etc/locale.conf
echo '127.0.0.1\\tlocalhost\\n::1\\tlocalhost\\n127.0.1.1\\t{hn}' > /etc/hosts
mkinitcpio -P
chsh -s /bin/fish
grub-install {iDevice}