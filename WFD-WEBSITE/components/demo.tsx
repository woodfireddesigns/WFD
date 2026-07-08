import { Navbar } from "@/components/ui/mini-navbar";

const DemoOne = () => {
  return (
    <div className="relative min-h-screen bg-[#0a0a0a] text-white font-sans overflow-hidden">
      {/* Background image — replace src with your own asset */}
      <div className="absolute inset-0">
        <img
          className="w-full h-full object-cover grayscale"
          src="https://images.unsplash.com/photo-1419242902214-272b3f66ee7a?w=1920&q=80"
          alt="Background — night sky"
        />
      </div>

      <Navbar />

      <main className="relative z-10 flex flex-col items-center justify-center h-screen text-center px-4 pt-24">
        <h1 className="text-8xl md:text-9xl font-bold text-white mb-4 tracking-tight drop-shadow-xl">
          MINI NAVBAR
        </h1>
        <p className="text-xl text-gray-300">
          Floating pill nav with animated links and mobile drawer.
        </p>
      </main>
    </div>
  );
};

export default DemoOne;
