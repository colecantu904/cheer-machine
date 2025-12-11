import { useEffect, useState } from "react";

interface NoteProps {
  passkey: string;
}

export default function Note({ passkey }: NoteProps) {
  const [message, setMessage] = useState("");

  useEffect(() => {
    // call the decrypt-message backend and pass the passkey
    async function getMessaage() {
      try {
        const apiUrl =
          process.env.NODE_ENV === "production"
            ? "https://cheer-machine.vercel.app"
            : "http://127.0.0.1:8000";

        const response = await fetch(
          `${apiUrl}/api/decrypt-message/${passkey}`
        );
        const data = await response.json();

        if (response.ok) {
          setMessage(data.message);
        } else {
          console.error("Failed to fetch decrypted message:", data.message);
        }
      } catch (error) {
        console.error("Error fetching decrypted message:", error);
      }
    }

    getMessaage();
  }, []);

  return (
    <div className="">
      <p className="text-white text-2xl md:text-3xl lg:text-4xl font-medium text-center leading-relaxed max-w-3xl ">
        {message}
      </p>
    </div>
  );
}
