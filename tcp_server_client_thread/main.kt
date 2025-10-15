import org.zeromq.ZMQ
import org.zeromq.ZContext
import java.util.Scanner

class TcpServer(private val port: Int = 8080) : Runnable {
    override fun run() {
        ZContext().use { context ->
            val socket = context.createSocket(ZMQ.REP).apply {
                bind("tcp://*:$port")
            }
            println("Server started on port $port")

            while (true) {
                val msg = socket.recvStr() ?: continue
                println("Server got: $msg")

                if (msg.equals("exit", true)) {
                    socket.send("goodbye")
                    println("Client disconnected")
                    continue
                }

                socket.send("ok")
            }
        }
    }
}

class TcpClient(
    private val host: String = "localhost",
    private val port: Int = 8080
) : Runnable {
    override fun run() {
        val scanner = Scanner(System.`in`)
        ZContext().use { context ->
            val socket = context.createSocket(ZMQ.REQ).apply {
                connect("tcp://$host:$port")
            }
            println("Connected to $host:$port (type 'exit' to quit)")

            while (true) {
                print("Enter message: ")
                val msg = scanner.nextLine().trim()
                if (msg.isEmpty()) continue

                socket.send(msg)
                val reply = socket.recvStr()
                println("Reply: $reply")

                if (msg.equals("exit", true)) break
            }
        }
        println("Client stopped")
    }
}

fun main() {
    println("Choose option:\n1. Server\n2. Client\n3. Both")
    when (readLine()?.trim()) {
        "1" -> Thread(TcpServer()).start()
        "2" -> Thread(TcpClient()).start()
        "3" -> {
            val server = Thread(TcpServer())
            val client = Thread {
                Thread.sleep(1000)
                TcpClient().run()
            }
            server.start()
            client.start()
            server.join(); client.join()
        }
        else -> println("Invalid choice")
    }
}
