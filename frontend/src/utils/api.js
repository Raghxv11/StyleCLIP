const convertImageToBase64 = (image) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => {
      resolve(reader.result.split(',')[1]);
    };
    reader.onerror = (error) => reject(error);
    reader.readAsDataURL(image);
  });
};

export const uploadClothingItem = async (image) => {
  try {
    const base64Image = await convertImageToBase64(image);

    const payload = {
      filename: image.name,
      image_base64: base64Image,
    };

    const response = await fetch("http://localhost:8000/clothing/upload", {
      method: "POST",
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error("Failed to upload clothing item");
    }

    return await response.json();
  } catch (error) {
    console.error("Error uploading clothing item:", error);
    throw error;
  }
};

export const tagClothingImage = async (image) => {
  try {
    const base64Image = await convertImageToBase64(image);

    const payload = {
      image_base64: base64Image,
    };

    const response = await fetch("http://localhost:8000/clothing/tag", {
      method: "POST",
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error("Failed to tag clothing image");
    }

    return await response.json();
  } catch (error) {
    console.error("Error tagging clothing image:", error);
    throw error;
  }
};

export const getSimilarItems = async (itemId, limit = 5) => {
  try {
    const response = await fetch(`http://localhost:8000/clothing/similar/${itemId}?limit=${limit}`);
    
    if (!response.ok) {
      throw new Error("Failed to get similar items");
    }
    
    return await response.json();
  } catch (error) {
    console.error("Error getting similar items:", error);
    throw error;
  }
};

// --------------------------
// Tinder-like App API Functions
// --------------------------

export const createUser = async (username, email) => {
  try {
    const response = await fetch("http://localhost:8000/clothing/users", {
      method: "POST",
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, email }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Failed to create user");
    }

    return await response.json();
  } catch (error) {
    console.error("Error creating user:", error);
    throw error;
  }
};

export const swipeItem = async (userId, clothingItemId, action) => {
  try {
    const response = await fetch("http://localhost:8000/clothing/swipe", {
      method: "POST",
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: userId,
        clothing_item_id: clothingItemId,
        action: action
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Failed to record swipe");
    }

    return await response.json();
  } catch (error) {
    console.error("Error recording swipe:", error);
    throw error;
  }
};

export const getUserPreferences = async (userId) => {
  try {
    const response = await fetch(`http://localhost:8000/clothing/users/${userId}/preferences`);
    
    if (!response.ok) {
      throw new Error("Failed to get user preferences");
    }
    
    return await response.json();
  } catch (error) {
    console.error("Error getting user preferences:", error);
    throw error;
  }
};

export const getUserFeed = async (userId, limit = 10) => {
  try {
    const response = await fetch(`http://localhost:8000/clothing/users/${userId}/feed?limit=${limit}`);
    
    if (!response.ok) {
      throw new Error("Failed to get user feed");
    }
    
    return await response.json();
  } catch (error) {
    console.error("Error getting user feed:", error);
    throw error;
  }
};

export const getNextItem = async (userId) => {
  try {
    const response = await fetch(`http://localhost:8000/clothing/users/${userId}/next`);
    
    if (!response.ok) {
      throw new Error("Failed to get next item");
    }
    
    return await response.json();
  } catch (error) {
    console.error("Error getting next item:", error);
    throw error;
  }
};
