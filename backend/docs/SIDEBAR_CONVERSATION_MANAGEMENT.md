# Sidebar Conversation Management

## Overview
The Sidebar component provides a comprehensive interface for managing medical consultations, including creating, renaming, and deleting conversations.

## Features

### 1. New Consultation Button
- Located at the top of the sidebar
- Allows users to start a new medical consultation instantly
- Uses a prominent blue button with a plus icon

### 2. Conversation List
- Displays previous medical consultations
- Sorted by most recent first
- Each conversation shows:
  - Chat bubble icon
  - Conversation title
  - Options menu

### 3. Conversation Management

#### 3.1 Options Menu
- Triggered by clicking the ellipsis (⋯) icon
- Provides two primary actions:
  1. **Rename Conversation**
  2. **Delete Conversation**

#### 3.2 Renaming a Conversation
- Click the ellipsis icon
- Select "Rename" from dropdown
- Edit title inline
- Confirm with ✓ or cancel with ✗
- Prevents empty titles

#### 3.3 Deleting a Conversation
- Click the ellipsis icon
- Select "Delete" from dropdown
- Prevents deleting the last conversation
- Automatically selects another conversation after deletion

## Technical Implementation

### State Management
```typescript
const [isHovered, setIsHovered] = useState<string | null>(null);
const [editingConversationId, setEditingConversationId] = useState<string | null>(null);
const [editTitle, setEditTitle] = useState<string>('');
const [activeOptionsId, setActiveOptionsId] = useState<string | null>(null);
```

### Key Functions
```typescript
// Delete a conversation
const handleDeleteConversation = (conversationId: string) => {
  if (conversations.length > 1) {
    deleteConversation(conversationId);
  }
};

// Rename a conversation
const handleRenameConversation = (conversationId: string) => {
  if (editTitle.trim()) {
    renameConversation(conversationId, editTitle.trim());
  }
};
```

## User Experience Considerations
- Smooth animations for interactions
- Intuitive dropdown menu
- Prevents destructive actions (like deleting last conversation)
- Responsive design
- Accessibility-friendly interactions

## Performance Optimizations
- Memoized context functions
- Efficient state management
- Minimal re-renders
- Local storage synchronization

## Future Improvements
- Add confirmation modal for deletion
- Implement conversation search
- Add conversation filtering options
- Enhance accessibility features

## Dependencies
- React Hooks
- Framer Motion
- Heroicons
- Context API

## Error Handling
- Prevents empty conversation titles
- Blocks deletion of the last conversation
- Graceful state management during interactions

## Accessibility
- Keyboard navigable
- Screen reader friendly
- High contrast design
- Semantic HTML structure

## Browser Compatibility
- Tested on modern browsers
- Responsive across desktop and mobile devices

## Security Considerations
- No sensitive data exposed in UI
- Controlled state mutations
- Sanitized user inputs

---

**Note**: This documentation provides an overview of the Sidebar Conversation Management system. Refer to the source code for the most up-to-date implementation details.
