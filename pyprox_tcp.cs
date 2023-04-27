using System;
using System.Net;
using System.Net.Sockets;
using System.Threading;
using System.IO;

class ThreadedServer
{
    private IPAddress host;
    private int port;
    private Socket sock;

    private const int listenPort = 2500;
    private const string cloudflareIP = "162.159.135.42";
    private const int cloudflarePort = 443;
    private const int fragmentLength = 77;
    private const double fragmentSleep = 0.2;
    private const int mySocketTimeout = 60;
    private const double firstTimeSleep = 0.01;
    private const double acceptTimeSleep = 0.01;

    public ThreadedServer(IPAddress host, int port)
    {
        this.host = host;
        this.port = port;
        this.sock = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
        this.sock.SetSocketOption(SocketOptionLevel.Socket, SocketOptionName.ReuseAddress, true);
        this.sock.Bind(new IPEndPoint(this.host, this.port));
    }

    public void Listen()
    {
        this.sock.Listen(128);
        while (true)
        {
            Socket clientSock = this.sock.Accept();
            clientSock.ReceiveTimeout = mySocketTimeout * 1000;
            Thread.Sleep(TimeSpan.FromSeconds(acceptTimeSleep));
            Thread threadUp = new Thread(() => MyUpstream(clientSock));
            threadUp.IsBackground = true;
            threadUp.Start();
        }
    }

    private void MyUpstream(Socket clientSock)
    {
        bool firstFlag = true;
        Socket backendSock = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
        backendSock.ReceiveTimeout = mySocketTimeout * 1000;

        while (true)
        {
            try
            {
                if (firstFlag)
                {
                    firstFlag = false;
                    Thread.Sleep(TimeSpan.FromSeconds(firstTimeSleep));
                    byte[] data = new byte[16384];
                    int received = clientSock.Receive(data);
                    Array.Resize(ref data, received);

                    if (data.Length > 0)
                    {
                        backendSock.Connect(cloudflareIP, cloudflarePort);
                        Thread threadDown = new Thread(() => MyDownstream(backendSock, clientSock));
                        threadDown.IsBackground = true;
                        threadDown.Start();
                        SendDataInFragment(data, backendSock);
                    }
                    else
                    {
                        throw new Exception("cli syn close");
                    }
                }
                else
                {
                    byte[] data = new byte[4096];
                    int received = clientSock.Receive(data);
                    Array.Resize(ref data, received);

                    if (data.Length > 0)
                    {
                        backendSock.Send(data);
                    }
                    else
                    {
                        throw new Exception("cli pipe close");
                    }
                }
            }
            catch (Exception e)
            {
                Thread.Sleep(TimeSpan.FromSeconds(2));
                clientSock.Close();
                backendSock.Close();
                return;
            }
        }
    }

    private void MyDownstream(Socket backendSock, Socket clientSock)
    {
        bool firstFlag = true;
        while (true)
        {
            try
            {
                byte[] data = new byte[firstFlag ? 16384 : 4096];
                int received = backendSock.Receive(data);
                Array.Resize(ref data, received);

                if (data.Length > 0)
                {
                    clientSock.Send(data);
                    firstFlag = false;
                }
                else
                {
                    throw new Exception("backend pipe close");
                }
            }
            catch (Exception e)
            {
                Thread.Sleep(TimeSpan.FromSeconds(2));
                backendSock.Close();
                clientSock.Close();
                return;
            }
        }
    }

    private void SendDataInFragment(byte[] data, Socket sock)
    {
        for (int i = 0; i < data.Length; i += fragmentLength)
        {
            byte[] fragmentData = new byte[Math.Min(fragmentLength, data.Length - i)];
            Array.Copy(data, i, fragmentData, 0, fragmentData.Length);
            sock.Send(fragmentData);
            Thread.Sleep(TimeSpan.FromSeconds(fragmentSleep));
        }
    }

    public static void Main()
    {
        Console.WriteLine("Now listening at: 127.0.0.1:" + listenPort);
        new ThreadedServer(IPAddress.Any, listenPort).Listen();
    }
}
