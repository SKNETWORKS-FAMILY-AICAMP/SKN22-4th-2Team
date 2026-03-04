import { Component, ReactNode } from 'react';
import { ErrorFallback } from './ErrorFallback';

interface Props {
    children: ReactNode;
}

interface State {
    hasError: boolean;
    errorTitle: string;
    errorMessage: string;
}

export class ErrorBoundary extends Component<Props, State> {
    public state: State = {
        hasError: false,
        errorTitle: '',
        errorMessage: ''
    };

    public static getDerivedStateFromError(error: Error): State {
        return {
            hasError: true,
            errorTitle: '예상치 못한 내부 오류가 발생했습니다 💥',
            errorMessage: error.message || '애플리케이션 렌더링 중 문제가 발생했습니다.'
        };
    }

    public handleReset = () => {
        this.setState({ hasError: false, errorTitle: '', errorMessage: '' });
        window.location.reload();
    };

    public render() {
        if (this.state.hasError) {
            return (
                <div className="min-h-screen p-8 flex flex-col items-center justify-center bg-gray-50">
                    <ErrorFallback
                        title={this.state.errorTitle}
                        message={this.state.errorMessage}
                        onRetry={this.handleReset}
                    />
                </div>
            );
        }

        return this.props.children;
    }
}
