// src/pages/CreatePost.jsx
import { useState } from "react";
import { useApi } from "../hooks/useApi";
import { toast } from "react-hot-toast";
import PageContainer from "../components/PageContainer";

export default function CreatePost() {
  const { request } = useApi();
  const [body, setBody] = useState("");
  const [hours, setHours] = useState(12);

  async function handleSubmit(e) {
    e.preventDefault();
    const id = Math.random().toString(36).slice(2);
    try {
      await request(`/create_post/${id}`, "POST", {
        body,
        voting_hours: hours,
      });
      toast.success("Post created");
      setBody("");
      setHours(12);
    } catch (err) {
      toast.error(err.message || "Failed to create post");
    }
  }

  return (
    <PageContainer>
      <div className="max-w-2xl mx-auto bg-[#1A2A20] p-6 rounded shadow">
        <h1 className="text-2xl font-bold text-[#7FAF92] mb-4">Create a New Post</h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block mb-1 text-[#E8E5DC]">Post Content</label>
            <textarea
              value={body}
              onChange={(e) => setBody(e.target.value)}
              rows={4}
              className="w-full p-2 rounded border bg-[#16221C] text-[#E8E5DC]"
              placeholder="Share your debate topic or opinion..."
              required
            />
          </div>
          <div>
            <label className="block mb-1 bg-[#16221C] text-[#E8E5DC]">Voting duration (hours)</label>
            <input
              type="number"
              value={hours}
              onChange={(e) => setHours(e.target.value)}
              className="w-full p-2 rounded border bg-[#16221C] text-[#E8E5DC]"
              min="1"
              max="72"
            />
          </div>
          <button
            type="submit"
            className="bg-[#7FAF92] text-black px-4 py-2 rounded hover:bg-[#5D749B]"
          >
            Submit
          </button>
        </form>
      </div>
    </PageContainer>
  );
}
