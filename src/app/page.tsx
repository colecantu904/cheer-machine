"use client";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Bracket from "./bracket";

export default function Home() {
  const [showForm, setShowForm] = useState(false);
  const [currentPasskey, setCurrentPasskey] = useState("");

  return (
    <div className="christmas-landing">
      {!currentPasskey ? (
        <>
          {/* Snowflakes */}
          <div className="snowflakes" aria-hidden="true">
            {[...Array(15)].map((_, i) => (
              <div key={i} className="snowflake">
                ❅
              </div>
            ))}
          </div>

          {/* Stars */}
          <div className="stars" aria-hidden="true">
            <div className="star" key={1}>
              ⭐
            </div>
          </div>

          {/* Main Content */}
          <main
            className={`main-content ${showForm ? "fadeOut" : "fadeInButton"}`}
          >
            <h1 className="christmas-title">Merry Christmas!</h1>

            <div className="h-15">
              {showForm ? (
                <div className="h-full max-w-[90vw]">
                  <form
                    className="h-full flex flex-row gap-1 w-full"
                    onSubmit={(e) => {
                      e.preventDefault();
                      // Handle passkey submission logic here)
                      setCurrentPasskey((e.target as any)[0].value);
                    }}
                  >
                    <input
                      type="password"
                      placeholder="Enter Passkey"
                      className="christmas-input"
                    />
                    <button type="submit" className="christmas-button">
                      {">"}
                    </button>
                  </form>
                </div>
              ) : (
                <button
                  className="christmas-button"
                  onClick={() => {
                    setShowForm(true);
                  }}
                >
                  Play
                </button>
              )}
            </div>

            <p className="christmas-text">made with ❤️ by Cole Cantu</p>
          </main>
        </>
      ) : (
        <div className="bracket-container">
          <Bracket passkey={currentPasskey} />
        </div>
      )}
    </div>
  );
}
