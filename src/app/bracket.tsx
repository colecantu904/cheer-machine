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
  const [image1, setImage1] = useState<string>("");
  const [image2, setImage2] = useState<string>("");
  const [vote, setVote] = useState<number | null>(null);

  // go over every 2 images, display, then add the winner to next round
  // if there is 1 image to vote on, it automatically goes to next round
  // when the list has only 1 left, return winner
  // on win, add a hearfelt note for her to read, and some cute styling
  const currentPairs = useRef<number[]>([]);
  const nextPairs = useRef<number[]>([]);
  const i = useRef<number>(0); // index in images array

  const handleReset = () => {
    // Reset logic here
    currentPairs.current = (Array.from(images.keys()) as number[]).sort(
      () => Math.random() - 0.5
    );
    nextPairs.current = [];
    setImage1(images[currentPairs.current[0]]);
    setImage2(images[currentPairs.current[1]]);
    i.current = 0;
    setVote(null);
    setWinner(null);
  };

  // Fetch images once on mount
  useEffect(() => {
    async function fetchImages() {
      try {
        const apiUrl =
          process.env.NODE_ENV === "production"
            ? "https://cheer-machine.vercel.app"
            : "http://127.0.0.1:8000";

        const response = await fetch(`${apiUrl}/api/decrypt/${passkey}`);
        const data = await response.json();

        const path_data = data.images;

        setImages(path_data);
        currentPairs.current = (Array.from(path_data.keys()) as number[]).sort(
          () => Math.random() - 0.5
        );
        setImage1(path_data[currentPairs.current[0]]);
        setImage2(path_data[currentPairs.current[1]]);
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

    console.log(currentPairs.current);
    console.log("Next Pairs:", nextPairs.current);
    console.log("Index:", i.current);

    if (i.current >= currentPairs.current.length) {
      // move to next round
      currentPairs.current = nextPairs.current.sort(() => Math.random() - 0.5);
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
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="flex gap-3">
          <div className="w-4 h-4 bg-blue-500 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
          <div className="w-4 h-4 bg-blue-500 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
          <div className="w-4 h-4 bg-blue-500 rounded-full animate-bounce"></div>
        </div>
      </div>
    );
  }

  return (
    <>
      {!winner ? (
        <div
          className="flex flex-col h-full justify-start pt-8"
          style={{ paddingTop: "24px", alignItems: "flex-end" }}
        >
          <div className="flex flex-col items-center gap-2 w-[95vw] h-[85vh] p-8 mt-8">
            <button
              onClick={() => setVote(1)}
              className="w-full h-1/2 max-w-xl"
            >
              <img
                className="rounded-sm w-full h-full object-cover"
                src={image1}
                alt="Image 1"
              />
            </button>
            {image2 && (
              <button
                onClick={() => setVote(2)}
                className="w-full h-1/2 max-w-xl"
              >
                <img
                  className="rounded-sm w-full h-full object-cover"
                  src={image2}
                  alt="Image 2"
                />
              </button>
            )}
          </div>
        </div>
      ) : (
        <div className="flex flex-col items-center gap-8">
          <div className="w-auto h-auto">
            <img
              className="w-full h-full object-contain"
              src={winner}
              alt="Winner"
            />
          </div>
          <button onClick={handleReset} className="christmas-button">
            Try Again?
          </button>
        </div>
      )}
    </>
  );
}
