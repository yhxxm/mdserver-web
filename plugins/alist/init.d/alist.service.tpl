[Unit]
Description=A file list program that supports multiple storage
After=network.target

[Service]
Type=simple
ExecStart={$SERVER_PATH}/alist/alist server
ExecReload=/bin/kill -USR2 $MAINPID
Restart=on-failure

[Install]
WantedBy=multi-user.target