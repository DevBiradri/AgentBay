"use client";
import React from "react";
import { AnimatedTooltip } from "../ui/animated-tooltip";
const people = [
  {
    id: 1,
    name: "Syed Shahriyar Ali",
    designation: "Software Engineer",
    image:
      "https://avatars.githubusercontent.com/u/70702829?v=4",
  },
  {
    id: 2,
    name: "Muhammad Shaheer Jamal",
    designation: "AI Engineer",
    image:
      "https://avatars.githubusercontent.com/u/112032384?v=4",
  },
  {
    id: 3,
    name: "Syed Zaid Ali",
    designation: "Python Developer",
    image:
      "https://shahriyarali.com/assets/images/zaid.jpg",
  },
  {
    id: 4,
    name: "Abdul Wasay Sarwar",
    designation: "AI/Ml Inspired",
    image:
      "https://avatars.githubusercontent.com/u/136677108?v=4",
  },
  {
    id: 5,
    name: "Muhammad Ibad Moin",
    designation: "MernStack / AI Developer",
    image:
      "https://avatars.githubusercontent.com/u/123115847?v=4",
  },

];

export function AnimatedTooltipPreview() {
  return (
    <div className="flex flex-row items-center justify-center mb-10 w-full">
      <AnimatedTooltip items={people} />
    </div>
  );
}
