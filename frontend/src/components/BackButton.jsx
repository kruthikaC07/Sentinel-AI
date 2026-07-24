import { ArrowLeft } from "lucide-react";
import { useNavigate } from "react-router-dom";

export default function BackButton({ label = "Back" }) {
  const navigate = useNavigate();
  return (
    <button className="secondary-button mb-5" type="button" onClick={() => navigate(-1)}>
      <ArrowLeft size={17} />
      {label}
    </button>
  );
}
