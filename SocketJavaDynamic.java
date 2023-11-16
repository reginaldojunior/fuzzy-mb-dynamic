import java.nio.ByteBuffer;
import java.nio.channels.ServerSocketChannel;
import java.nio.channels.SocketChannel;
import java.util.List;
import java.util.Random;
import java.util.concurrent.TimeUnit;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.net.InetSocketAddress;

public class SocketJavaDynamic {
    private static long lastMinuteUpdate = 0;
    private static int ips = 0;

    public static boolean passouUmMinuto(long started, long current) {
        double elapsedSeconds = (current - started) / 1000.0;

        System.out.println("Elapsed Seconds: " + elapsedSeconds);

        return elapsedSeconds > 60;
    }

    public static int oscilarInstanciasPorSegundo(int limit, int maxRate, long started, long current) {
        final double PERCENT_10 = 0.10;
        final double PERCENT_50 = 0.50;
        final double PERCENT_90 = 0.90;

        if (passouUmMinuto(lastMinuteUpdate, current)) {
            Random random = new Random();
            int choice = random.nextInt(3);
            if (choice == 0) {
                ips = (int) (maxRate * PERCENT_10);
            } else if (choice == 1) {
                ips = (int) (maxRate * PERCENT_50);
            } else {
                ips = (int) (maxRate * PERCENT_90);
            }
            lastMinuteUpdate = current;
        }

        System.out.println("Limit Per Second: " + ips);

        // Gere um número aleatório com base no limite por segundo
        Random random = new Random();
        int ipsToSend = random.nextInt(ips);

        return ipsToSend;
    }

    public static void main(String[] args) throws IOException, InterruptedException {
        if (args.length != 4) {
            System.out.println("Usage: ServerProducer <ip> <port> <file> <Rate of instances per second>");
            System.exit(1);
        }

        String ip = args[0];
        int port = Integer.parseInt(args[1]);
        String filename = args[2];
        int maxRate = Integer.parseInt(args[3]);

        int instancesSent = 0;

        List<String> lines = Files.readAllLines(Paths.get(filename));
        System.out.println("read " + lines.size() + " lines to memory from file " + filename + ".");
        ServerSocketChannel serverSocketChannel = ServerSocketChannel.open();
        serverSocketChannel.configureBlocking(true);
        serverSocketChannel.bind(new InetSocketAddress(ip, port));
        System.out.println("ServerSocketChannel awaiting connections..." + serverSocketChannel.getLocalAddress());
        int i = 0;

        SocketChannel socketChannel = serverSocketChannel.accept();
        System.out.println("Connection from " + socketChannel + "!");

        serverSocketChannel.configureBlocking(false);
        boolean minuteComplete = false;

        if (socketChannel != null) {
            socketChannel.configureBlocking(false);

            boolean readingHeader = true;
            while (readingHeader) {
                String line = lines.get(i);
                if (line.contains("@data")) {
                    readingHeader = false;
                }
                i++;
            }

            String msg = "";
            boolean keepGoing = true;
            long startTime = 0;
            ByteBuffer buffer = ByteBuffer.allocate(1048576);
            int limit = lines.size();

            long startingAll = System.currentTimeMillis();
            long countMinute = System.currentTimeMillis();
            int ipb = 0;

            while (i < limit && keepGoing) {
                startTime = System.nanoTime();
                ipb = oscilarInstanciasPorSegundo(limit, maxRate, countMinute, System.currentTimeMillis());

                if (passouUmMinuto(countMinute, System.currentTimeMillis())) {
                    countMinute = System.currentTimeMillis();
                }

                int numInst = 0;

                while (numInst < ipb && i < limit) {
                    msg = lines.get(i++) + "#";
                    buffer.flip();
                    buffer = ByteBuffer.wrap(msg.getBytes());

                    try {
                        socketChannel.write(buffer);
                    } catch (IOException ex) {
                        System.out.println("Closed by client!");
                        keepGoing = false;
                        break;
                    }

                    numInst++;
                    instancesSent++;
                }

                long justSent = System.nanoTime();
                long elapsed = TimeUnit.NANOSECONDS.toMillis(justSent - startTime);
                long sleepTime = elapsed > 0 && elapsed < 1000 ? 1000 - elapsed : 1000;

                Thread.sleep(sleepTime);

                if (!keepGoing) {
                    break;
                }

                if ((System.currentTimeMillis() - startingAll) / 1000F > 600) { // trocar o 600 por uma constante LIMIT_MAX_EXECUTION
                    keepGoing = false;
                }
            }

            double totalSpent = (System.currentTimeMillis() - startingAll) / 1000.0;

            if (keepGoing) {
                msg = "$$";
                buffer.flip();
                buffer = ByteBuffer.wrap(msg.getBytes());
                if (socketChannel.isOpen()) {
                    socketChannel.write(buffer);
                }
            }

            System.out.println("\nTotal Time Producer (s): " + totalSpent);
            System.out.println("Total instances Producer: " + instancesSent);
            System.out.println("Producer Rate (inst per second): " + instancesSent / totalSpent);

            System.out.println("Closing socket and terminating program.");
            socketChannel.configureBlocking(true);
            socketChannel.close();
        }

        serverSocketChannel.close();
    }
}
