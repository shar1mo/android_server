#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>

#define PORT 8080
#define BUFFER_SIZE 1024

int main(void) {
  int sock = 0;
  struct sockaddr_in serv_addr;
  char buffer[BUFFER_SIZE] = {0};
  char message[BUFFER_SIZE];

  if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
    printf("\nSocket creation error\n");
    return EXIT_FAILURE;
  }

  serv_addr.sin_family = AF_INET;
  serv_addr.sin_port = htons(PORT);

  if (inet_pton(AF_INET, "127.0.0.1", &serv_addr.sin_addr) <= 0) {
    printf("Invalid address\n");
    return EXIT_FAILURE;
  }

  if (connect(sock, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0) {
    printf("\nConnection failed\n");
    return EXIT_FAILURE;
  }

  printf("Connected to server\n");
  printf("Type 'exit' to quit\n");

  while (1) {
    printf("Enter message: ");
    fgets(message, BUFFER_SIZE, stdin);
        
    message[strcspn(message, "\n")] = 0;
        
    if (strlen(message) == 0) {
      continue;
    }

    send(sock, message, strlen(message), 0);
    printf("Message sent: %s\n", message);

    if (strcmp(message, "exit") == 0) {
      printf("Exiting...\n");
      break;
    }

    int valread = read(sock, buffer, BUFFER_SIZE - 1);
    if (valread > 0) {
      buffer[valread] = '\0';
      printf("Server response: %s\n", buffer);
    } else {
      printf("Server disconnected\n");
      break;
    }
        
    memset(buffer, 0, BUFFER_SIZE);
  }

  close(sock);
  printf("Connection closed\n");

  return EXIT_SUCCESS;
}