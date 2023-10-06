import java.nio.file.*;
import java.security.acl.LastOwnerException;
import java.util.List;
import java.util.Random;
import java.io.IOException;
import java.net.Socket;
import java.util.ArrayList;
import java.io.*;
import java.net.ConnectException;
import java.lang.InterruptedException;
import java.util.concurrent.TimeUnit;
import java.net.InetAddress;
import java.net.ServerSocket;
import java.net.InetSocketAddress;
import java.nio.ByteBuffer;
import java.nio.channels.AsynchronousServerSocketChannel;
import java.nio.channels.AsynchronousSocketChannel;
import java.util.concurrent.Future;
import java.nio.channels.SocketChannel;
import java.nio.channels.ServerSocketChannel;

public class SocketJavaDynamic {

    public static int oscilarInstanciasPorSegundo(int limit) {
        double limitPerSegundo = limit * 0.05;

        Random random = new Random();
        int ips = random.nextInt((int) limitPerSegundo) + 1;

        return ips;
    }

    public static int oscilarTempoEntreEnvioDeMensagens(int limit) {
        Random random = new Random();
        int segundos = random.nextInt(limit);

        return segundos;
    }

    public static void main(String[] args) throws IOException, InterruptedException {
        if (args.length != 3) {
            System.out.println("Usage: ServerProducer <ip> <port> <file> <Rate of instances per second>");
            System.exit(1);
        }

        String ip = args[0];
        int port = Integer.parseInt(args[1]);
        String filename = args[2];

        int instancesSent = 0;

        // load all file to memory
        List<String> lines = Files.readAllLines(Paths.get(filename));
        System.out.println("read " + lines.size() + " lines to memory from file " + filename + ".");
        ServerSocketChannel serverSocketChannel = ServerSocketChannel.open();
        serverSocketChannel.configureBlocking(true);
        serverSocketChannel.bind(new InetSocketAddress(ip, port));
        System.out.println("ServerSocketChannel awaiting connections..." + serverSocketChannel.getLocalAddress());
        int i = 0;
        SocketChannel socketChannel = serverSocketChannel.accept(); // blocking
        System.out.println("Connection from " + socketChannel + "!");

        serverSocketChannel.configureBlocking(false);
        if (socketChannel != null) {
            socketChannel.configureBlocking(false);

            boolean reading_header = true;
            while (reading_header) {
                String l = lines.get(i);
                if (l.contains("@data"))
                    reading_header = false;
                i++;
            }

            String msg = "";

            boolean keep_going = true;

            long startTime = 0;
            ByteBuffer buffer = ByteBuffer.allocate(1048576); //1048576

            int limit = lines.size();

            long startingAll = System.currentTimeMillis();
            long lastSuccessfullStep = 0;
            int ips = 0;
            int ipb = 0;
            int segundos = 0;
            while (i < limit && keep_going) {
                segundos = 0;
                startTime = System.nanoTime();
                // We want to send a fixed per second rate, but divided in smaller chunks
                // we use IPB (IPS/5) to send 5 smaller chunks
                // create the chunk by sending instances without delay (Strings)
                // while (instances.size() < IPB && i < lines.size()) {
                // send chunk

                ips = oscilarInstanciasPorSegundo(limit);
                ipb = ips / 5;

                int num_inst = 0;
                while (num_inst < ipb && i < limit) {                    
                    msg = lines.get(i++) + "#";
                    buffer.flip();
                    buffer = ByteBuffer.wrap(msg.getBytes());

                    try {
                        socketChannel.write(buffer);
                    } catch (IOException ex) {
                        System.out.println("Closed by client!");
                        keep_going = false;
                        break;
                    }

                    num_inst++;
                    instancesSent++;
                }

                //System.out.println("Sent [ " + (num_inst) + " ] messages.");

                long justSent = System.nanoTime();
                long elapsed = TimeUnit.NANOSECONDS.toMillis(justSent - startTime);
                long sl = elapsed > 0 && elapsed < 1000 ? 1000 - elapsed : 1000;

                Thread.sleep(sl);

                if (!keep_going)
                    break;

                if ((System.currentTimeMillis() - startingAll) / 1000F > 120) {
                    keep_going = false;
                }
            }

            double totalSpent = (System.currentTimeMillis() - startingAll) / 1000.0;

            // send finish message
            if (keep_going) {
                msg = "$$";
                buffer.flip();
                buffer = ByteBuffer.wrap(msg.getBytes());
                if (socketChannel.isOpen())
                    socketChannel.write(buffer);
            }

            System.out.println("\nTotal Time Producer (s): " + totalSpent);
            System.out.println("Total instances Producer: " + instancesSent);
            System.out.println("Producer Rate (inst per second): " + instancesSent/totalSpent);

            // close socket
            System.out.println("Closing socket and terminating program.");
            socketChannel.configureBlocking(true);
            socketChannel.close();
        }

        serverSocketChannel.close();
    }
}
