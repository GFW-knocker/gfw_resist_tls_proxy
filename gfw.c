#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <pthread.h>

#ifdef __linux__
#include <sys/resource.h>
#endif

#define MY_SOCKET_TIMEOUT 60
#define FIRST_TIME_SLEEP 10000 // microseconds, i.e. 0.01 seconds
#define ACCEPT_TIME_SLEEP 10000 // microseconds, i.e. 0.01 seconds
#define LISTEN_PORT 2500
#define CLOUDFLARE_IP "162.159.135.42"
#define CLOUDFLARE_PORT 443
#define L_FRAGMENT 77
#define FRAGMENT_SLEEP 200000 // microseconds, i.e. 0.2 seconds

int my_socket_timeout = MY_SOCKET_TIMEOUT;
int first_time_sleep = FIRST_TIME_SLEEP;
int accept_time_sleep = ACCEPT_TIME_SLEEP;

void *my_upstream(void *arg);
void *my_downstream(void *arg);
void send_data_in_fragment(unsigned char *data, int len, int sock);

int main(int argc, char **argv) {
    int listen_sock;
    struct sockaddr_in server_addr;

#ifdef __linux__
    printf("os is linux\n");

    struct rlimit limits;
    if (getrlimit(RLIMIT_NOFILE, &limits) == -1) {
        perror("getrlimit");
        exit(EXIT_FAILURE);
    }
    printf("max_num_open_socket: %ld -> %d\n", limits.rlim_cur, 127000);

    limits.rlim_cur = 127000;
    limits.rlim_max = 128000;
    if (setrlimit(RLIMIT_NOFILE, &limits) == -1) {
        perror("setrlimit");
        exit(EXIT_FAILURE);
    }
#endif

    listen_sock = socket(AF_INET, SOCK_STREAM, 0);
    if (listen_sock == -1) {
        perror("socket");
        exit(EXIT_FAILURE);
    }

    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(LISTEN_PORT);

    if (bind(listen_sock, (struct sockaddr *) &server_addr, sizeof(server_addr)) == -1) {
        perror("bind");
        exit(EXIT_FAILURE);
    }

    if (listen(listen_sock, 128) == -1) {
        perror("listen");
        exit(EXIT_FAILURE);
    }

    printf("Now listening at: %s:%d\n", "127.0.0.1", LISTEN_PORT);

    while (1) {
        struct sockaddr_in client_addr;
        socklen_t client_addrlen = sizeof(client_addr);
        int client_sock = accept(listen_sock, (struct sockaddr *) &client_addr, &client_addrlen);
        if (client_sock == -1) {
            perror("accept");
            continue;
        }

        pthread_t thread_up;
        if (pthread_create(&thread_up, NULL, my_upstream, (void *) (intptr_t) client_sock) != 0) {
            perror("pthread_create");
            close(client_sock);
            continue;
        }

        if (pthread_detach(thread_up) != 0) {
            perror("pthread_detach");
            close(client_sock);
            continue;
        }
    }

    return 0;
}

void *my_upstream(void *arg) {
    int client_sock = (intptr_t) arg;
    int backend_sock;
    unsigned char buf[16384];

    fd_set read_fds;
    struct timeval timeout;

    int first_flag = 1;
    while (1) {
        FD_ZERO(&read_fds);
        FD_SET(client_sock, &read_fds);

        timeout.tv_sec = my_socket_timeout;
        timeout.tv_usec = 0;

        int nready = select(client_sock + 1, &read_fds, NULL, NULL, &timeout);
        if (nready == -1) {
            perror("select");
            break;
        } else if (nready == 0) {
            printf("client_sock timed out\n");
            break;
        }

        if (FD_ISSET(client_sock, &read_fds)) {
            if (first_flag) {
                first_flag = 0;

                usleep(first_time_sleep);

                ssize_t nrecv = recv(client_sock, buf, sizeof(buf), 0);
                if (nrecv == -1) {
                    perror("recv");
                    break;
                } else if (nrecv == 0) {
                    fprintf(stderr, "cli syn close\n");
                    break;
                }

                backend_sock = socket(AF_INET, SOCK_STREAM,0);
                if (backend_sock == -1) {
                    perror("socket");
                    break;
                }

                struct sockaddr_in backend_addr;
                memset(&backend_addr, 0, sizeof(backend_addr));
                backend_addr.sin_family = AF_INET;
                backend_addr.sin_port = htons(CLOUDFLARE_PORT);

                if (inet_pton(AF_INET, CLOUDFLARE_IP, &backend_addr.sin_addr) != 1) {
                    fprintf(stderr, "inet_pton failed\n");
                    close(backend_sock);
                    break;
                }

                pthread_t thread_down;
                if (pthread_create(&thread_down, NULL, my_downstream, (void *) (intptr_t) backend_sock) != 0) {
                    perror("pthread_create");
                    close(backend_sock);
                    break;
                }

                if (pthread_detach(thread_down) != 0) {
                    perror("pthread_detach");
                    close(backend_sock);
                    break;
                }

                send_data_in_fragment(buf, nrecv, backend_sock);
            } else {
                ssize_t nrecv = recv(client_sock, buf, sizeof(buf), 0);
                if (nrecv == -1) {
                    perror("recv");
                    break;
                } else if (nrecv == 0) {
                    fprintf(stderr, "cli pipe close\n");
                    break;
                }

                if (send(backend_sock, buf, nrecv, 0) != nrecv) {
                    perror("send");
                    break;
                }
            }
        }
    }

    close(client_sock);
    close(backend_sock);
    return NULL;
}

void *my_downstream(void *arg) {
    int backend_sock = (intptr_t) arg;
    int client_sock;
    unsigned char buf[16384];

    fd_set read_fds;
    struct timeval timeout;

    int first_flag = 1;
    while (1) {
        FD_ZERO(&read_fds);
        FD_SET(backend_sock, &read_fds);

        timeout.tv_sec = my_socket_timeout;
        timeout.tv_usec = 0;

        int nready = select(backend_sock + 1, &read_fds, NULL, NULL, &timeout);
        if (nready == -1) {
            perror("select");
            break;
        } else if (nready == 0) {
            printf("backend_sock timed out\n");
            break;
        }

        if (FD_ISSET(backend_sock, &read_fds)) {
            if (first_flag) {
                first_flag = 0;

                ssize_t nrecv = recv(backend_sock, buf, sizeof(buf), 0);
                if (nrecv == -1) {
                    perror("recv");
                    break;
                } else if (nrecv == 0) {
                    fprintf(stderr, "backend pipe close at first\n");
                    break;
                }

                if (send(client_sock, buf, nrecv, 0) != nrecv) {
                    perror("send");
                    break;
                }
            } else {
                ssize_t nrecv = recv(backend_sock, buf, sizeof(buf), 0);
                if (nrecv == -1) {
                    perror("recv");
                    break;
                } else if (nrecv == 0) {
                    fprintf(stderr, "backend pipe close\n");
                    break;
                }

                if (send(client_sock, buf, nrecv, 0) != nrecv) {
                    perror("send");
                    break;
                }
            }
        }
    }

    close(backend_sock);
    close(client_sock);
    return NULL;
}

void send_data_in_fragment(unsigned char *data, int len, int sock) {
    for (int i = 0; i < len; i += L_FRAGMENT) {
        int nsend = send(sock, &data[i], L_FRAGMENT, 0);
        if (nsend == -1) {
            perror("send");
            break;
        }
        printf("send %d bytes\n", nsend);
        usleep(FRAGMENT_SLEEP);
    }
    printf("----------finish------------\n");
}


