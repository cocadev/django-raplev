from django.urls import path

from . import views
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                
app_name = 'theme'
urlpatterns = [
    path('pages/', views.Pages.as_view(), name='pages'),
    path('set-country/', views.SetCountry.as_view(), name='set-country'),

    # Login Not Required
    path('', views.Index.as_view(), name='index'),
    path('index/', views.Index.as_view()),
    path('blog-listing/', views.BlogListing.as_view(), name='blog-listing'),
    path('blog-detail/', views.BlogDetail.as_view(), name='blog-detail'),
    path('contact/', views.Contact.as_view(), name='contact'),
    path('support-center/', views.SupportCenter.as_view(), name='support-center'),
    path('submit-ticket/', views.SubmitTicket.as_view(), name='submit-ticket'),
    path('ticket-details/', views.TicketDetails.as_view(), name='ticket-details'),

    # Not Logged In
    path('login/', views.Login.as_view(), name='login'),
    path('register/', views.Register.as_view(), name='register'),
    path('forgot-password/', views.ForgotPassword.as_view(), name='forgot-password'),
    path('forgot-password-email/', views.ForgotPasswordEmail.as_view(), name='forgot-password-email'),
    path('forgot-password-phone/', views.ForgotPasswordPhone.as_view(), name='forgot-password-phone'),
    path('resend-forgot-password-email/', views.ResendConfirmEmail.as_view(), name='resend-forgot-password-email'), #for forgot password with email
    path('resend-forgot-password-phone/', views.ResendConfirmPhone.as_view(), name='resend-forgot-password-phone'), #for forgot password with phone
    path('confirm-forgot-password-phone-code/', views.ConfirmForgotPWPhoneCode.as_view(), name='resend-forgot-password-phone-code'), #for forgot password get phone code
    path('confirm-forgot-password-email/', views.ConfirmForgotPWEmail.as_view(), name='confirm-forgot-password-email'), #for reset password with email
    path('confirm-forgot-password-phone/', views.ConfirmForgotPWPhone.as_view(), name='confirm-forgot-password-phone'), #for reset password with email
    path('reset-password/', views.ResetPassword.as_view(), name='reset-password'),
    
    # Login Required
    path('logout/', views.logout, name='logout'),
    path('resend-verify-email/', views.ResendVerifyEmail.as_view(), name='resend-verify-email'), #for email verify
    path('resend-verify-phone/', views.ResendVerifyPhone.as_view(), name='resend-verify-phone'), #for phone verify
    path('verify-phone-code/', views.VerifyPhoneCode.as_view(), name='resend-confirm-phone-code'), #for verify phone code
    path('verify-email/', views.VerifyEmail.as_view(), name='verify-email'), #for verify email
    path('verify-phone/', views.VerifyPhone.as_view(), name='verify-phone'), #for verify phone

    path('get-badges/', views.get_badges, name='get-badges'),

    path('new-offer/', views.NewOffer.as_view(), name='new-offer'),
    path('profile-overview/', views.ProfileOverview.as_view(), name='profile-overview'),
    path('received-offers/', views.ReceivedOffers.as_view(), name='received-offers'),
    path('buy-sell-coins/', views.BuySellCoins.as_view(), name='buy-sell-coins'),
    path('funding/', views.Funding.as_view(), name='funding'),
    path('user-public-profile/', views.UserPublicProfile.as_view(), name='user-public-profile'),
    path('offer-activity/', views.OfferActivity.as_view(), name='offer-activity'),
    path('edit-offer/', views.EditOffer.as_view(), name='edit-offer'),
    path('all-offers/', views.AllOffers.as_view(), name='all-offers'),
    path('offer-detail/', views.OfferDetail.as_view(), name='offer-detail'),
    path('offer-listing/', views.OfferListing.as_view(), name='offer-listing'),
    # path('buy-listing/', views.BuyListing.as_view(), name='buy-listing'),
    # path('sell-listing/', views.SellListing.as_view(), name='sell-listing'),
    path('single-offer-detail/', views.SingleOfferDetail.as_view(), name='single-offer-detail'),
    path('initiate-trade/', views.InitiateTrade.as_view(), name='initiate-trade'),
    path('caculate-trade/', views.caculateTrade, name='caculate-trade'),
    path('trade-processed/', views.TradeProcessed.as_view(), name='trade-processed'),
    path('proof-of-transaction/', views.ProofOfTransaction.as_view(), name='proof-of-transaction'),
    path('trade-complete/', views.TradeComplete.as_view(), name='trade-complete'),
    path('send-counter-offer/', views.SendCounterOffer.as_view(), name='send-counter-offer'),
    path('watch-list/', views.WatchList.as_view(), name='watch-list'),
    path('flag-feedback/', views.FlagFeedback.as_view(), name='flag-feedback'),
    path('leave-review/', views.LeaveReview.as_view(), name='leave-review'),
    path('independent-escrow/', views.IndependentEscrow.as_view(), name='independent-escrow'),
    path('vendor-proof-of-transaction/', views.VendorProofOfTransaction.as_view(), name='vendor-proof-of-transaction'),
    path('vpof-gift-card-steps/', views.VPOFGiftCardSteps.as_view(), name='vpof-gift-card-steps'),
    path('vpof-gift-card-open-code/', views.VPOFGiftCardOpenCode.as_view(), name='vpof-gift-card-open-code'),
    path('send/', views.Send.as_view(), name='send'),
    path('receive/', views.Receive.as_view(), name='receive'),
    path('trade-history/', views.TradeHistory.as_view(), name='trade-history'),
    path('saved-wallet/', views.SavedWallet.as_view(), name='saved-wallet'),
    path('my-balance/', views.MyBalance.as_view(), name='my-balance'),
    path('withdraw-funds/', views.WithdrawFunds.as_view(), name='withdraw-funds'),
    path('deposits/', views.Deposits.as_view(), name='deposits'),
    path('withdrawals/', views.Withdrawals.as_view(), name='withdrawals'),
    path('messages/', views.Messages.as_view(), name='messages'),
    path('invitation-in-message/', views.InvitationInMessage.as_view(), name='invitation-in-message'),
    path('id-verification/', views.IdVerification.as_view(), name='id-verification'),
    path('notifications/', views.Notifications.as_view(), name='notifications'),
    path('vendors/', views.Vendors.as_view(), name='vendors'),
    path('referrals/', views.Referrals.as_view(), name='referrals'),

    path('buy/', views.Buy.as_view(), name='buy'), #landing page as multi language.
    path('add-message/', views.AddMessage.as_view(), name='buy'), 
    path('upload/', views.UploadView.as_view(), name='upload'),

    path('mft/', views.makeing_fake_trade, name='make-fake-transaction'),

]
