export async function getReadableLocation() {
  const manualFallback = () => {
    const location = window.prompt("Enter the incident location or nearest landmark:");
    return location ? { address: location, latitude: "", longitude: "" } : null;
  };

  if (!navigator.geolocation) {
    return manualFallback();
  }

  try {
    const position = await new Promise((resolve, reject) => {
      navigator.geolocation.getCurrentPosition(resolve, reject, {
        enableHighAccuracy: true,
        timeout: 9000,
        maximumAge: 30000
      });
    });
    const latitude = position.coords.latitude.toFixed(6);
    const longitude = position.coords.longitude.toFixed(6);
    const address = await reverseGeocode(latitude, longitude);
    if (address) {
      return { address, latitude, longitude };
    }
    const manualAddress = window.prompt("GPS was captured, but the address could not be resolved. Enter the nearest area, street, or landmark:");
    return manualAddress ? { address: manualAddress, latitude, longitude } : null;
  } catch {
    return manualFallback();
  }
}

async function reverseGeocode(latitude, longitude) {
  try {
    const url = `https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${encodeURIComponent(latitude)}&lon=${encodeURIComponent(longitude)}`;
    const response = await fetch(url, {
      headers: {
        Accept: "application/json"
      }
    });
    if (!response.ok) return "";
    const data = await response.json();
    const address = data.address || {};
    const parts = [
      address.neighbourhood || address.suburb || address.village || address.town || address.city_district,
      address.city || address.town || address.village || address.county,
      address.state,
      address.country
    ].filter(Boolean);
    return parts.length ? parts.join(", ") : data.display_name;
  } catch {
    return "";
  }
}
