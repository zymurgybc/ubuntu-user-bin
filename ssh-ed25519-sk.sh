
# Create a host SSH key authenticated by 2FA with Yubikey
# https://www.youtube.com/watch?v=PjDFk8xdtGw
ssh-keygen -t ed25519-sk -C "$(hostname)-$(date +'%Y-%m-%d')-yubikey1"
