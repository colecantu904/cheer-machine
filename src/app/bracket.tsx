import { useState, useEffect, useRef } from "react";

interface BracketProps {
  passkey: string;
}

export default function Bracket({ passkey }: BracketProps) {
  // takes the key, decodes all the images, stores in
  // array, intitates bracket, iterate through bracket

  const [images, setImages] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [winner, setWinner] = useState<string | null>(null);
  const [image1, setImage1] = useState<string | null>(null);
  const [image2, setImage2] = useState<string | null>(null);
  const [vote, setVote] = useState<number | null>(null);

  // go over every 2 images, display, then add the winner to next round
  // if there is 1 image to vote on, it automatically goes to next round
  // when the list has only 1 left, return winner
  // on win, add a hearfelt note for her to read, and some cute styling
  const currentPairs = useRef<number[]>([]);
  const nextPairs = useRef<number[]>([]);
  const i = useRef<number>(0); // index in images array

  // Fetch images once on mount
  useEffect(() => {
    async function fetchImages() {
      try {
        const apiUrl = "https://cheer-machine.vercel.app";
        //   process.env.NODE_ENV === "production"
        //     ? "https://cheer-machine.vercel.app"
        //     : "http://127.0.0.1:8000";

        const response = await fetch(`${apiUrl}/api/decrypt/${passkey}`);
        const data = await response.json();

        const path_data = data.images;

        setImages(path_data);
        currentPairs.current = Array.from(path_data.keys());
        setImage1(path_data[0]);
        setImage2(path_data[1]);
      } catch (error) {
        console.error("Failed to fetch images:", error);
      } finally {
        setIsLoading(false);
      }
    }

    fetchImages();
  }, [passkey]);

  useEffect(() => {
    if (vote === null || images.length === 0) return;

    console.log("Vote cast for image:", vote);

    if (currentPairs.current.length === 1) {
      // we have a winner
      setWinner(images[currentPairs.current[0]]);
      return;
    }

    // add the winner to next round
    const winnerIndex = vote === 1 ? i.current : i.current + 1;
    nextPairs.current.push(currentPairs.current[winnerIndex]);

    i.current += 2;

    if (i.current >= currentPairs.current.length) {
      // move to next round
      currentPairs.current = nextPairs.current;
      nextPairs.current = [];
      i.current = 0;

      if (currentPairs.current.length === 1) {
        // we have a winner
        setWinner(images[currentPairs.current[0]]);
        return;
      }
    }

    setImage1(images[currentPairs.current[i.current]]);
    setImage2(images[currentPairs.current[i.current + 1]]);

    console.log("Current Pairs:", currentPairs.current);
    console.log("Next Pairs:", nextPairs.current);
    console.log("Index:", i.current);

    setVote(null);
  }, [vote, images]);

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <>
      {!winner ? (
        <div className="flex flex-col gap-2 w-[95vw] h-[95vh] p-4">
          <button onClick={() => setVote(1)} className="w-full h-1/2">
            <img
              className="rounded-sm w-full h-full object-cover"
              src={image1!}
              alt="Image 1"
            />
          </button>
          <button onClick={() => setVote(2)} className="w-full h-1/2">
            <img
              className="rounded-sm w-full h-full object-cover"
              src={image2!}
              alt="Image 2"
            />
          </button>
        </div>
      ) : (
        <div className="aspect-auto">
          <img
            className="rounded-sm w-full h-full object-cover"
            src={winner}
            alt="Winner"
          />
        </div>
      )}
    </>
  );
}
