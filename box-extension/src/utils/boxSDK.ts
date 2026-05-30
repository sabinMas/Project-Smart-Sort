/**
 * Box SDK integration utilities
 * Handles Box context, authentication, and API interactions
 */

interface BoxItem {
  id: string;
  name: string;
  type: 'file' | 'folder' | 'web_link';
}

interface BoxFile extends BoxItem {
  type: 'file';
  size: number;
  created_at: string;
  modified_at: string;
}

interface BoxContext {
  fileId: string;
  fileName: string;
  folderId: string;
  userId: string;
  accessToken: string;
}

/**
 * Get the current Box context (file ID, auth token, etc.)
 * This is called automatically by Box when the extension is initialized
 */
export const getBoxContext = (): Promise<BoxContext> => {
  return new Promise((resolve, reject) => {
    // Box SDK automatically provides context via window.postMessage
    // The extension is initialized with context in a parent frame message
    const handleMessage = (event: MessageEvent) => {
      if (event.data?.type === 'BOX_CONTEXT') {
        window.removeEventListener('message', handleMessage);
        resolve({
          fileId: event.data.fileId,
          fileName: event.data.fileName,
          folderId: event.data.folderId,
          userId: event.data.userId,
          accessToken: event.data.accessToken,
        });
      }
    };

    window.addEventListener('message', handleMessage);

    // Fallback timeout if no message received
    setTimeout(() => {
      window.removeEventListener('message', handleMessage);
      reject(new Error('Box context not received within timeout'));
    }, 5000);

    // Signal that we're ready to receive context
    window.parent?.postMessage({ type: 'BOX_EXTENSION_READY' }, '*');
  });
};

/**
 * Get file details from Box API
 */
export const getFileDetails = async (
  fileId: string,
  accessToken: string
): Promise<BoxFile> => {
  const response = await fetch(`https://api.box.com/2.0/files/${fileId}`, {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${accessToken}`,
      'Accept': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch file details: ${response.statusText}`);
  }

  return response.json();
};

/**
 * Update file metadata in Box
 */
export const updateFileMetadata = async (
  fileId: string,
  metadata: Record<string, any>,
  accessToken: string
): Promise<void> => {
  const response = await fetch(
    `https://api.box.com/2.0/files/${fileId}/metadata/global/properties`,
    {
      method: 'PUT',
      headers: {
        Authorization: `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(metadata),
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to update metadata: ${response.statusText}`);
  }
};

/**
 * Move file to different folder in Box
 */
export const moveFile = async (
  fileId: string,
  parentFolderId: string,
  accessToken: string
): Promise<BoxFile> => {
  const response = await fetch(`https://api.box.com/2.0/files/${fileId}`, {
    method: 'PUT',
    headers: {
      Authorization: `Bearer ${accessToken}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      parent: {
        id: parentFolderId,
      },
    }),
  });

  if (!response.ok) {
    throw new Error(`Failed to move file: ${response.statusText}`);
  }

  return response.json();
};

/**
 * Create a task in Box (requires Task resource)
 */
export const createTask = async (
  fileId: string,
  assignedToId: string,
  dueAt: string,
  message: string,
  accessToken: string
): Promise<any> => {
  const response = await fetch('https://api.box.com/2.0/tasks', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${accessToken}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      item: {
        type: 'file',
        id: fileId,
      },
      action: 'review',
      message: message,
      due_at: dueAt,
      assign_to: {
        id: assignedToId,
      },
    }),
  });

  if (!response.ok) {
    throw new Error(`Failed to create task: ${response.statusText}`);
  }

  return response.json();
};

/**
 * Get user by email from Box API
 */
export const getUserByEmail = async (
  email: string,
  accessToken: string
): Promise<any> => {
  const response = await fetch(
    `https://api.box.com/2.0/users?filter_term=${encodeURIComponent(email)}`,
    {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${accessToken}`,
        'Accept': 'application/json',
      },
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to search user: ${response.statusText}`);
  }

  const data = await response.json();
  return data.entries?.[0] || null;
};

export default {
  getBoxContext,
  getFileDetails,
  updateFileMetadata,
  moveFile,
  createTask,
  getUserByEmail,
};
