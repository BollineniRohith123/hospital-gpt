# Metropolitan Advanced Medical Center - Frontend

## Overview
This is the frontend application for the Metropolitan Advanced Medical Center, built with Next.js, React, and Tailwind CSS. The application provides a robust, modern interface for medical professionals to interact with hospital systems.

## Features
- 🏥 Comprehensive Hospital Dashboard
- 💬 Medical AI Assistant
- 📊 Advanced Analytics
- 👥 Patient Management System
- 🔒 Secure Authentication

## Technology Stack
- Next.js 14
- React 18
- TypeScript
- Tailwind CSS
- Heroicons
- Framer Motion

## Prerequisites
- Node.js 18+
- npm or pnpm

## Installation
1. Clone the repository
2. Install dependencies:
   ```bash
   pnpm install
   ```

3. Run the development server:
   ```bash
   pnpm dev
   ```

## Project Structure
- `app/`: Next.js page components
- `components/`: Reusable React components
- `context/`: React context providers
- `public/`: Static assets

## Environment Configuration
Create a `.env.local` file with the following variables:
```
NEXT_PUBLIC_API_URL=your_backend_api_url
NEXT_PUBLIC_HOSPITAL_NAME=Metropolitan Advanced Medical Center
```

## Deployment
```bash
pnpm build
pnpm start
```

## Security Considerations
- All patient data is anonymized
- Implements role-based access control
- Follows HIPAA compliance guidelines

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
Proprietary - Metropolitan Advanced Medical Center

## Contact
Medical IT Department
email: medical-it@metropolitanhospital.com
