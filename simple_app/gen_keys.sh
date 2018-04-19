for i in {0..3}; do
  openssl genrsa -out client''$i''_private.pem 512
  openssl rsa -in client''$i''_private.pem -pubout -out client''$i''_public.pem
  openssl genrsa -out server''$i''_private.pem 512
  openssl rsa -in server''$i''_private.pem -pubout -out server''$i''_public.pem
done
